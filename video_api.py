"""
main.py

FastAPI wrapper around the full video-generator pipeline:
  1. generate_video_script.py  -> script
  2. fetch_stock_footage.py    -> script + stock clips
  3. generate_voiceover.py     -> script + voiceover audio
  4. assemble_video.py         -> final .mp4

Exposes:
  POST /generate-video   -> kicks off generation, returns a job_id
  GET  /jobs/{job_id}    -> check status / get the final video URL

Usage:
    uvicorn main:app --reload

Requires:
    pip install fastapi uvicorn python-dotenv
    (plus everything the four pipeline scripts already require)

NOTE ON ASYNC PROCESSING:
Video generation takes real time (LLM call + footage search + TTS +
FFmpeg render) — too long for a single HTTP request to wait on. This
version uses FastAPI's BackgroundTasks for a simple in-memory job queue,
which is fine for local testing and a single-server deployment. Once you
have real traffic, swap this for Celery + Redis so jobs survive a server
restart and can scale across multiple workers.
"""

import uuid
import shutil
from pathlib import Path
from enum import Enum

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from generate_video_script import generate_script
from fetch_stock_footage import attach_footage_to_script
from generate_voiceover import generate_voiceovers_for_script
from assemble_video import assemble_video

import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="AI Video Generator")

JOBS_DIR = Path("jobs")
JOBS_DIR.mkdir(exist_ok=True)


class JobStatus(str, Enum):
    PENDING = "pending"
    GENERATING_SCRIPT = "generating_script"
    FETCHING_FOOTAGE = "fetching_footage"
    GENERATING_VOICEOVER = "generating_voiceover"
    ASSEMBLING_VIDEO = "assembling_video"
    DONE = "done"
    FAILED = "failed"


class GenerateVideoRequest(BaseModel):
    topic: str
    duration_seconds: int = 30
    tone: str = "punchy and direct"


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    error: str | None = None


# In-memory job store. Fine for single-process local testing.
# Replace with a real database (Postgres, Redis) before deploying for real users.
JOBS: dict[str, dict] = {}


def run_pipeline(job_id: str, topic: str, duration_seconds: int, tone: str) -> None:
    """
    Runs all four pipeline steps in sequence for one job, updating
    JOBS[job_id]["status"] as it progresses so the client can poll.
    """
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    original_cwd = Path.cwd()

    try:
        import os as _os
        _os.chdir(job_dir)  # keep each job's intermediate files isolated

        anthropic_key = os.environ["ANTHROPIC_API_KEY"]
        pexels_key = os.environ["PEXELS_API_KEY"]
        elevenlabs_key = os.environ["ELEVENLABS_API_KEY"]

        JOBS[job_id]["status"] = JobStatus.GENERATING_SCRIPT
        script = generate_script(topic, duration_seconds, tone)

        JOBS[job_id]["status"] = JobStatus.FETCHING_FOOTAGE
        script = attach_footage_to_script(script, pexels_key)

        JOBS[job_id]["status"] = JobStatus.GENERATING_VOICEOVER
        script = generate_voiceovers_for_script(script, elevenlabs_key)

        JOBS[job_id]["status"] = JobStatus.ASSEMBLING_VIDEO
        final_path = assemble_video(script)

        JOBS[job_id]["status"] = JobStatus.DONE
        JOBS[job_id]["video_path"] = str((job_dir / final_path).resolve())

    except Exception as e:
        JOBS[job_id]["status"] = JobStatus.FAILED
        JOBS[job_id]["error"] = str(e)

    finally:
        _os.chdir(original_cwd)


@app.post("/generate-video", response_model=JobResponse)
def generate_video(request: GenerateVideoRequest, background_tasks: BackgroundTasks):
    """
    Kicks off video generation for the given topic. Returns immediately
    with a job_id — poll GET /jobs/{job_id} to check progress.
    """
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": JobStatus.PENDING, "error": None, "video_path": None}

    background_tasks.add_task(
        run_pipeline, job_id, request.topic, request.duration_seconds, request.tone
    )

    return JobResponse(job_id=job_id, status=JobStatus.PENDING)


@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job_status(job_id: str):
    """Returns the current status of a generation job."""
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResponse(job_id=job_id, status=job["status"], error=job["error"])


@app.get("/jobs/{job_id}/video")
def get_job_video(job_id: str):
    """Returns the final video file once the job is done."""
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != JobStatus.DONE:
        raise HTTPException(status_code=409, detail=f"Job not finished yet (status: {job['status']})")

    return FileResponse(job["video_path"], media_type="video/mp4", filename="video.mp4")


@app.get("/")
def root():
    return {"message": "AI Video Generator API is running. POST to /generate-video to start."}
