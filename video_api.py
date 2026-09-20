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
    pip install fastapi uvicorn python-dotenv pymongo
    (plus everything the four pipeline scripts already require)

NOTE ON ASYNC PROCESSING:
Video generation takes real time (LLM call + footage search + TTS +
FFmpeg render) — too long for a single HTTP request to wait on. This
version uses FastAPI's BackgroundTasks for a simple job queue, which is
fine for a single-server deployment. Once you have real traffic, swap
this for Celery + Redis so jobs can scale across multiple workers.

NOTE ON JOB STORAGE:
Job status is stored in MongoDB (if MONGODB_URI is set) rather than an
in-memory dict, so a server redeploy no longer wipes job records — a job
interrupted mid-run will correctly show "failed" instead of vanishing
into "Job not found". A redeploy still kills the actual FFmpeg process
running that job, so an interrupted job needs to be re-submitted; this
change just makes that visible instead of silently losing the record.
If MONGODB_URI isn't set, falls back to the original in-memory dict so
local development without Mongo still works.
"""

import os
import uuid
import shutil
from pathlib import Path
from enum import Enum
from typing import Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pymongo import MongoClient

from generate_video_script import generate_script
from fetch_stock_footage import attach_footage_to_script
from generate_voiceover import generate_voiceovers_for_script
from assemble_video import assemble_video
from generate_marketing import attach_marketing_to_script

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="AI Video Generator")

JOBS_DIR = Path("jobs")
JOBS_DIR.mkdir(exist_ok=True)


class JobStatus(str, Enum):
    PENDING = "pending"
    GENERATING_SCRIPT = "generating_script"
    FETCHING_FOOTAGE = "fetching_footage"
    GENERATING_MARKETING = "generating_marketing"
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


# ============================================================
# JOB STORAGE — MongoDB if configured, otherwise an in-memory
# fallback dict so local dev without Mongo still works.
# ============================================================
MONGODB_URI = os.environ.get("MONGODB_URI")
_mongo_client = None
_jobs_collection = None
if MONGODB_URI:
    try:
        _mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        _mongo_client.admin.command("ping")
        _jobs_collection = _mongo_client["video_generator"]["jobs"]
        print("MongoDB connected — job status will survive redeploys.")
    except Exception as e:
        print(f"MongoDB connection failed: {e} — falling back to in-memory job storage.")
        _mongo_client = None
        _jobs_collection = None

# Only used if MongoDB isn't configured/reachable.
_JOBS_FALLBACK: dict[str, dict] = {}


def create_job(job_id: str) -> None:
    doc = {"_id": job_id, "status": JobStatus.PENDING.value, "error": None, "video_path": None}
    if _jobs_collection is not None:
        _jobs_collection.insert_one(doc)
    else:
        _JOBS_FALLBACK[job_id] = doc


def update_job(job_id: str, **fields) -> None:
    """Update one or more fields on a job (e.g. status="done", video_path=...)."""
    if _jobs_collection is not None:
        _jobs_collection.update_one({"_id": job_id}, {"$set": fields})
    else:
        _JOBS_FALLBACK.setdefault(job_id, {}).update(fields)


def get_job(job_id: str) -> Optional[dict]:
    if _jobs_collection is not None:
        return _jobs_collection.find_one({"_id": job_id})
    return _JOBS_FALLBACK.get(job_id)


def run_pipeline(job_id: str, topic: str, duration_seconds: int, tone: str) -> None:
    """
    Runs all five pipeline steps in sequence for one job, updating the
    job's status in storage as it progresses so the client can poll.
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
        gemini_key = os.environ.get("GEMINI_API_KEY")  # optional — marketing step degrades gracefully without it

        update_job(job_id, status=JobStatus.GENERATING_SCRIPT.value)
        script = generate_script(topic, duration_seconds, tone)

        update_job(job_id, status=JobStatus.FETCHING_FOOTAGE.value)
        script = attach_footage_to_script(script, pexels_key)

        update_job(job_id, status=JobStatus.GENERATING_MARKETING.value)
        script = attach_marketing_to_script(script, gemini_key)
        # attach_marketing_to_script never raises — on failure it just sets
        # script["marketing"] = None, so the pipeline continues regardless.
        update_job(job_id, marketing=script.get("marketing"))

        update_job(job_id, status=JobStatus.GENERATING_VOICEOVER.value)
        script = generate_voiceovers_for_script(script, elevenlabs_key)

        update_job(job_id, status=JobStatus.ASSEMBLING_VIDEO.value)
        final_path = assemble_video(script)

        update_job(
            job_id,
            status=JobStatus.DONE.value,
            video_path=str((job_dir / final_path).resolve()),
        )

    except Exception as e:
        update_job(job_id, status=JobStatus.FAILED.value, error=str(e))

    finally:
        _os.chdir(original_cwd)


@app.post("/generate-video", response_model=JobResponse)
def generate_video(request: GenerateVideoRequest, background_tasks: BackgroundTasks):
    """
    Kicks off video generation for the given topic. Returns immediately
    with a job_id — poll GET /jobs/{job_id} to check progress.
    """
    job_id = str(uuid.uuid4())
    create_job(job_id)

    background_tasks.add_task(
        run_pipeline, job_id, request.topic, request.duration_seconds, request.tone
    )

    return JobResponse(job_id=job_id, status=JobStatus.PENDING)


@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job_status(job_id: str):
    """Returns the current status of a generation job."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResponse(job_id=job_id, status=job["status"], error=job.get("error"))


@app.get("/jobs/{job_id}/video")
def get_job_video(job_id: str):
    """Returns the final video file once the job is done."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != JobStatus.DONE.value:
        raise HTTPException(status_code=409, detail=f"Job not finished yet (status: {job['status']})")

    return FileResponse(job["video_path"], media_type="video/mp4", filename="video.mp4")


@app.get("/jobs/{job_id}/marketing")
def get_job_marketing(job_id: str):
    """Returns the platform-specific marketing copy (YouTube, TikTok,
    Instagram, X, email, LinkedIn) generated for this job. Available as
    soon as the marketing-generation step completes — no need to wait for
    the full video to finish assembling."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    marketing = job.get("marketing")
    if marketing is None:
        raise HTTPException(
            status_code=404,
            detail="Marketing copy not available yet for this job (still generating, or generation failed).",
        )

    return marketing


@app.get("/")
def root():
    return {"message": "AI Video Generator API is running. POST to /generate-video to start."}
