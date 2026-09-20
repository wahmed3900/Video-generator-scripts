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
from datetime import datetime, timezone

from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pymongo import MongoClient
import stripe

from generate_video_script import generate_script
from fetch_stock_footage import attach_footage_to_script
from generate_voiceover import generate_voiceovers_for_script
from assemble_video import assemble_video
from generate_marketing import attach_marketing_to_script

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="AI Video Generator")

# Comma-separated list of allowed frontend origins, e.g.:
#   ALLOWED_ORIGINS=https://video-generator-scripts-frontend.vercel.app,http://localhost:3000
# Falls back to this project's actual known frontend + local dev origins if unset.
_default_origins = "https://video-generator-scripts-frontend.vercel.app,http://localhost:3000,http://127.0.0.1:5500"
ALLOWED_ORIGINS = [
    o.strip() for o in os.environ.get("ALLOWED_ORIGINS", _default_origins).split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    email: str  # required — used for the free-tier usage limit and subscription check


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    error: str | None = None


class CheckoutRequest(BaseModel):
    email: str
    success_url: str
    cancel_url: str


class CheckoutResult(BaseModel):
    checkout_url: str


class SubscriptionStatus(BaseModel):
    email: str
    active: bool
    videos_used_this_month: int
    free_videos_per_month: int
    dev_mode: bool


class VideoSummary(BaseModel):
    job_id: str
    topic: str
    status: JobStatus
    created_at: str
    error: str | None = None
    has_video: bool
    has_marketing: bool


# ============================================================
# JOB STORAGE — MongoDB if configured, otherwise an in-memory
# fallback dict so local dev without Mongo still works.
# ============================================================
MONGODB_URI = os.environ.get("MONGODB_URI")
_mongo_client = None
_jobs_collection = None
_subscriptions_collection = None
_usage_collection = None
if MONGODB_URI:
    try:
        _mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        _mongo_client.admin.command("ping")
        _jobs_collection = _mongo_client["video_generator"]["jobs"]
        _subscriptions_collection = _mongo_client["video_generator"]["subscriptions"]
        _usage_collection = _mongo_client["video_generator"]["usage"]
        print("MongoDB connected — job status will survive redeploys.")
    except Exception as e:
        print(f"MongoDB connection failed: {e} — falling back to in-memory job storage.")
        _mongo_client = None
        _jobs_collection = None
        _subscriptions_collection = None
        _usage_collection = None

# Only used if MongoDB isn't configured/reachable.
_JOBS_FALLBACK: dict[str, dict] = {}


def create_job(job_id: str, email: str, topic: str) -> None:
    doc = {
        "_id": job_id,
        "status": JobStatus.PENDING.value,
        "error": None,
        "video_path": None,
        "email": email.lower().strip(),
        "topic": topic,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if _jobs_collection is not None:
        _jobs_collection.insert_one(doc)
    else:
        _JOBS_FALLBACK[job_id] = doc


def list_jobs_for_email(email: str, limit: int = 50) -> list:
    """Returns this email's video-generation history, newest first."""
    email = email.lower().strip()
    if _jobs_collection is not None:
        cursor = _jobs_collection.find({"email": email}).sort("created_at", -1).limit(limit)
        return list(cursor)
    matches = [job for job in _JOBS_FALLBACK.values() if job.get("email") == email]
    matches.sort(key=lambda j: j.get("created_at", ""), reverse=True)
    return matches[:limit]


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


# ============================================================
# STRIPE — subscription billing ($35/mo unlimited after the free tier)
# ============================================================
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY
else:
    print("STRIPE_SECRET_KEY missing — /create-checkout-session will fail")

# ============================================================
# FREE TIER — limited videos/month before the paywall kicks in.
# Without MongoDB configured, usage can't be tracked reliably, so access
# is left open (dev mode) rather than blocking people on a broken config.
# ============================================================
FREE_VIDEOS_PER_MONTH = int(os.environ.get("FREE_VIDEOS_PER_MONTH", "3"))


def _current_month_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def has_active_subscription(email: str) -> bool:
    if _subscriptions_collection is None:
        return False  # no DB — treated as free tier, not "unlimited", so usage limits still apply
    doc = _subscriptions_collection.find_one({"email": email.lower().strip(), "status": "active"})
    return doc is not None


def get_usage_count(email: str) -> int:
    if _usage_collection is None:
        return 0
    doc = _usage_collection.find_one({"email": email.lower().strip(), "month": _current_month_key()})
    return doc["count"] if doc else 0


def increment_usage(email: str) -> None:
    if _usage_collection is None:
        return
    _usage_collection.update_one(
        {"email": email.lower().strip(), "month": _current_month_key()},
        {"$inc": {"count": 1}},
        upsert=True,
    )


def check_and_record_usage(email: str) -> None:
    """Raises HTTPException(402) if the free limit is hit and there's no active subscription.
    Otherwise records this video against the caller's monthly usage count."""
    if has_active_subscription(email):
        return  # unlimited — no usage tracking needed

    if _usage_collection is None:
        return  # no DB configured — dev mode, don't block anyone

    used = get_usage_count(email)
    if used >= FREE_VIDEOS_PER_MONTH:
        raise HTTPException(
            status_code=402,
            detail=(
                f"Free tier limit reached ({FREE_VIDEOS_PER_MONTH} videos/month). "
                "Use /create-checkout-session to subscribe for unlimited videos."
            ),
        )
    increment_usage(email)


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

    Gated behind the free-tier monthly limit (or an active subscription).
    """
    if not request.email.strip():
        raise HTTPException(status_code=400, detail="email is required")

    check_and_record_usage(request.email)  # raises 402 if the free limit is hit

    job_id = str(uuid.uuid4())
    create_job(job_id, request.email, request.topic)

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


@app.get("/videos", response_model=list[VideoSummary])
def list_videos(email: str):
    """Returns this editor's full video-generation history, newest first —
    the 'multiple videos per editor' dashboard view. Each entry shows
    enough to decide whether to check its status, download the video, or
    grab its marketing copy, without fetching every job's full detail."""
    if not email.strip():
        raise HTTPException(status_code=400, detail="email is required")

    jobs = list_jobs_for_email(email)
    return [
        VideoSummary(
            job_id=job["_id"],
            topic=job.get("topic", ""),
            status=job["status"],
            created_at=job.get("created_at", ""),
            error=job.get("error"),
            has_video=job.get("video_path") is not None,
            has_marketing=job.get("marketing") is not None,
        )
        for job in jobs
    ]


@app.get("/")
def root():
    return {"message": "AI Video Generator API is running. POST to /generate-video to start."}


# ============================================================
# STRIPE ENDPOINTS
# ============================================================

@app.post("/create-checkout-session", response_model=CheckoutResult)
def create_checkout_session(req: CheckoutRequest):
    """Creates a Stripe Checkout session for the $35/mo unlimited subscription."""
    if not STRIPE_SECRET_KEY or not STRIPE_PRICE_ID:
        raise HTTPException(status_code=500, detail="Stripe is not configured on the server.")
    if not req.email.strip():
        raise HTTPException(status_code=400, detail="email is required")

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
            customer_email=req.email,
            success_url=req.success_url,
            cancel_url=req.cancel_url,
            client_reference_id=req.email.lower(),
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {e}")

    return CheckoutResult(checkout_url=session.url)


# NOTE: this path must exactly match the endpoint URL configured in
# Stripe Dashboard -> Developers -> Webhooks for THIS service (separate
# from any other project's webhook — each service needs its own).
@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Stripe webhook secret not configured on the server.")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid signature: {e}")

    if _subscriptions_collection is None:
        # Can't record it, but acknowledge receipt so Stripe doesn't retry forever.
        return {"received": True, "warning": "No database configured — subscription not recorded."}

    try:
        if event["type"] == "checkout.session.completed":
            s = event["data"]["object"]
            email = (s.get("customer_email") or s.get("client_reference_id") or "").lower()
            if email:
                _subscriptions_collection.update_one(
                    {"email": email},
                    {"$set": {"status": "active", "customer_id": s.get("customer")}},
                    upsert=True,
                )
        elif event["type"] in ("customer.subscription.deleted", "customer.subscription.paused"):
            cust = event["data"]["object"].get("customer")
            if cust:
                _subscriptions_collection.update_one(
                    {"customer_id": cust}, {"$set": {"status": "canceled"}}
                )
    except Exception as e:
        print(f"Webhook processing error: {e}")

    return {"received": True}


@app.get("/subscription-status", response_model=SubscriptionStatus)
def subscription_status(email: str):
    """Lets the frontend show remaining free videos / subscription state
    before someone tries to generate a video and hits a 402."""
    if not email.strip():
        raise HTTPException(status_code=400, detail="email is required")

    return SubscriptionStatus(
        email=email,
        active=has_active_subscription(email),
        videos_used_this_month=get_usage_count(email),
        free_videos_per_month=FREE_VIDEOS_PER_MONTH,
        dev_mode=_usage_collection is None,
    )
