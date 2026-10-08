"""
generate_voiceover.py

Step 3 of the video-generator pipeline. Takes script_with_footage.json
(produced by fetch_stock_footage.py) and generates a voiceover audio file
for each scene's narration using Google Cloud Text-to-Speech.

Authentication:
    No API key needed. On Cloud Run, the service's built-in service
    account is used automatically. For local runs, sign in once with:
        gcloud auth application-default login
    The "Cloud Text-to-Speech API" must be enabled in the Google Cloud project.

Usage:
    python generate_voiceover.py

Requires:
    pip install google-cloud-texttospeech mutagen python-dotenv
    script_with_footage.json in the same directory (produced by step 2)

Optional environment variables:
    GOOGLE_TTS_VOICE           Voice name (default: en-US-Neural2-J)
    GOOGLE_TTS_FALLBACK_VOICE  Used if the main voice is rejected (default: en-US-Standard-J)
    GOOGLE_TTS_LANGUAGE        Language code (default: derived from the voice name)
    GOOGLE_TTS_SPEAKING_RATE   0.25-4.0 (default: 1.05, slightly brisk for short-form video)

Output:
    - One .mp3 file per scene, saved to ./audio/scene_<order>.mp3
    - script_with_audio.json — same structure as input, plus an
      "audio_path" and "actual_duration_seconds" field per scene

Robustness features:
    - Retries transient Google errors with exponential backoff
    - Falls back to a Standard voice if the chosen voice is rejected
    - Cleans LLM artifacts (markdown, stage directions, emoji, URLs) from narration
    - Splits long narration to stay under Google's per-request size limit
    - Writes audio atomically and verifies the file is non-empty
    - Always sets a duration (measured, or estimated from word count)
    - Clear, actionable error messages for auth, API-disabled and quota problems
"""

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional; environment variables can be set another way

from google.api_core import exceptions as google_exceptions
from google.auth import exceptions as auth_exceptions
from google.cloud import texttospeech

logger = logging.getLogger("generate_voiceover")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

# ============================================================
# CONFIG
# ============================================================
# Browse voices at https://cloud.google.com/text-to-speech/docs/voices
DEFAULT_VOICE_ID = os.environ.get("GOOGLE_TTS_VOICE", "en-US-Neural2-J")
FALLBACK_VOICE_ID = os.environ.get("GOOGLE_TTS_FALLBACK_VOICE", "en-US-Standard-J")

AUDIO_OUTPUT_DIR = Path("audio")

# Google TTS accepts up to 5,000 bytes of text per request. Stay under it
# with headroom; longer narration is split on sentence boundaries.
MAX_REQUEST_BYTES = 4500

MAX_ATTEMPTS = 4
REQUEST_TIMEOUT_SECONDS = 60
WORDS_PER_SECOND_ESTIMATE = 2.5  # ~150 wpm, used only if the audio can't be measured

RETRYABLE_ERRORS = (
    google_exceptions.ServiceUnavailable,
    google_exceptions.DeadlineExceeded,
    google_exceptions.InternalServerError,
    google_exceptions.TooManyRequests,
    google_exceptions.Aborted,
)


class VoiceoverError(RuntimeError):
    """Raised with a user-readable message when voiceover generation fails.
    The message ends up in the job's error field and is shown in the UI."""


# ============================================================
# CLIENT
# ============================================================
_client: Optional[texttospeech.TextToSpeechClient] = None


def _get_client() -> texttospeech.TextToSpeechClient:
    """Creates the TTS client once and reuses it across scenes and jobs."""
    global _client
    if _client is None:
        try:
            _client = texttospeech.TextToSpeechClient()
        except auth_exceptions.DefaultCredentialsError as e:
            raise VoiceoverError(
                "Google Cloud credentials not found. On Cloud Run this is automatic; "
                "locally, run: gcloud auth application-default login"
            ) from e
    return _client


# ============================================================
# SETTINGS HELPERS
# ============================================================
def _language_from_voice(voice_id: str) -> str:
    """'en-US-Neural2-J' -> 'en-US'."""
    override = os.environ.get("GOOGLE_TTS_LANGUAGE")
    if override:
        return override
    parts = voice_id.split("-")
    return "-".join(parts[:2]) if len(parts) >= 2 else "en-US"


def _speaking_rate() -> float:
    try:
        rate = float(os.environ.get("GOOGLE_TTS_SPEAKING_RATE", "1.05"))
    except ValueError:
        rate = 1.05
    return min(4.0, max(0.25, rate))


# ============================================================
# TEXT CLEANUP + SPLITTING
# ============================================================
_EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\u200d\ufe0f]",
    flags=re.UNICODE,
)


def clean_narration(text: str) -> str:
    """Removes things an LLM-written script may contain that shouldn't be
    read aloud: stage directions, markdown, emoji, URLs, hashtags."""
    if not text:
        return ""
    t = str(text)
    t = re.sub(r"\[[^\]]*\]", " ", t)              # [pause], [upbeat music]
    t = re.sub(r"\((?:pause|beat|music|sfx)[^)]*\)", " ", t, flags=re.IGNORECASE)
    t = re.sub(r"https?://\S+", " ", t)            # URLs
    t = re.sub(r"[*_`~#>]+", " ", t)               # markdown symbols, hashtag marks
    t = _EMOJI_RE.sub(" ", t)                       # emoji
    t = re.sub(r"^\s*(narrator|voiceover|vo)\s*:\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _split_text(text: str, max_bytes: int = MAX_REQUEST_BYTES) -> list[str]:
    """Splits narration into chunks under the per-request byte limit,
    breaking on sentence boundaries where possible."""
    if len(text.encode("utf-8")) <= max_bytes:
        return [text]

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, current = [], ""
    for sentence in sentences:
        candidate = f"{current} {sentence}".strip()
        if len(candidate.encode("utf-8")) <= max_bytes:
            current = candidate
            continue
        if current:
            chunks.append(current)
        # A single very long sentence: hard-split it by words.
        while len(sentence.encode("utf-8")) > max_bytes:
            piece = ""
            for word in sentence.split():
                if len(f"{piece} {word}".strip().encode("utf-8")) > max_bytes:
                    break
                piece = f"{piece} {word}".strip()
            if not piece:  # one enormous "word" — split by characters
                piece = sentence[: max_bytes // 4]
            chunks.append(piece)
            sentence = sentence[len(piece):].strip()
        current = sentence
    if current:
        chunks.append(current)
    return chunks


# ============================================================
# SYNTHESIS
# ============================================================
def _synthesize_once(text: str, voice_id: str) -> bytes:
    """One TTS request with retries on transient errors."""
    client = _get_client()
    request_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=_language_from_voice(voice_id),
        name=voice_id,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=_speaking_rate(),
    )

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.synthesize_speech(
                input=request_input,
                voice=voice,
                audio_config=audio_config,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            if not response.audio_content:
                raise VoiceoverError("Google Text-to-Speech returned empty audio.")
            return response.audio_content

        except RETRYABLE_ERRORS as e:
            if attempt == MAX_ATTEMPTS:
                raise VoiceoverError(
                    f"Google Text-to-Speech is temporarily unavailable (tried {MAX_ATTEMPTS} times). "
                    "Please try again in a minute."
                ) from e
            delay = 2 ** attempt  # 2s, 4s, 8s
            logger.warning("TTS attempt %d failed (%s); retrying in %ds", attempt, type(e).__name__, delay)
            time.sleep(delay)

        except google_exceptions.PermissionDenied as e:
            raise VoiceoverError(
                "Google Text-to-Speech permission denied. Enable the 'Cloud Text-to-Speech API' "
                "in this Google Cloud project (APIs & Services → Library)."
            ) from e

        except google_exceptions.Unauthenticated as e:
            raise VoiceoverError(
                "Google Text-to-Speech could not authenticate. Check the Cloud Run service account."
            ) from e

        except google_exceptions.ResourceExhausted as e:
            raise VoiceoverError(
                "Google Text-to-Speech quota reached. Check quotas in the Google Cloud console, "
                "or try again later."
            ) from e

    raise VoiceoverError("Google Text-to-Speech failed unexpectedly.")


def _synthesize(text: str, voice_id: str) -> bytes:
    """Synthesizes text with the chosen voice, falling back to a Standard
    voice if Google rejects the chosen one (e.g. a typo in GOOGLE_TTS_VOICE)."""
    try:
        return _synthesize_once(text, voice_id)
    except google_exceptions.InvalidArgument as e:
        if voice_id != FALLBACK_VOICE_ID:
            logger.warning("Voice '%s' rejected (%s); falling back to '%s'", voice_id, e, FALLBACK_VOICE_ID)
            try:
                return _synthesize_once(text, FALLBACK_VOICE_ID)
            except google_exceptions.InvalidArgument as e2:
                raise VoiceoverError(
                    f"Google Text-to-Speech rejected the request with both voices "
                    f"('{voice_id}' and '{FALLBACK_VOICE_ID}'). Details: {e2}"
                ) from e2
        raise VoiceoverError(f"Google Text-to-Speech rejected the request. Details: {e}") from e


# ============================================================
# FILE + DURATION
# ============================================================
def _write_atomically(data: bytes, output_path: Path) -> None:
    """Writes to a temp file then renames, so a crash never leaves a
    half-written .mp3 that the assembly step would choke on."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    with open(tmp_path, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, output_path)
    if output_path.stat().st_size == 0:
        raise VoiceoverError(f"Voiceover file {output_path.name} was written but is empty.")


def get_audio_duration_seconds(file_path: Path) -> Optional[float]:
    """Measures an MP3's duration with mutagen. Returns None if it can't be read."""
    try:
        from mutagen.mp3 import MP3
        length = MP3(file_path).info.length
        return round(length, 2) if length and length > 0 else None
    except Exception as e:
        logger.warning("Could not measure duration of %s: %s", file_path, e)
        return None


def _estimate_duration_seconds(text: str) -> float:
    words = len(text.split())
    return round(max(1.0, words / (WORDS_PER_SECOND_ESTIMATE * _speaking_rate())), 2)


# ============================================================
# PUBLIC API (used by video_api.py)
# ============================================================
def generate_voice_clip(text: str, api_key: Optional[str], voice_id: str, output_path: Path) -> str:
    """
    Synthesizes a single piece of narration and saves it to output_path.

    Args:
        text: The narration text to speak.
        api_key: Unused. Kept so existing callers don't need to change;
                 Google Cloud authenticates via the service account.
        voice_id: Google TTS voice name, e.g. "en-US-Neural2-J".
        output_path: Where to save the resulting .mp3 file.

    Returns:
        The cleaned text that was actually spoken.
    """
    cleaned = clean_narration(text)
    if not cleaned:
        raise VoiceoverError(f"Narration is empty after cleanup — cannot generate {output_path.name}.")

    audio = b"".join(_synthesize(chunk, voice_id) for chunk in _split_text(cleaned))
    _write_atomically(audio, output_path)
    return cleaned


def generate_voiceovers_for_script(script: dict, api_key: Optional[str] = None,
                                   voice_id: str = DEFAULT_VOICE_ID) -> dict:
    """
    For each scene in the script, generates a voiceover clip and attaches
    its file path and duration.

    The api_key argument is accepted but ignored, so video_api.py can keep
    calling generate_voiceovers_for_script(script, elevenlabs_key) unchanged.
    """
    if not isinstance(script, dict):
        raise VoiceoverError("Script is not in the expected format.")
    scenes = script.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise VoiceoverError("Script has no scenes to generate voiceovers for.")

    voice_id = (voice_id or DEFAULT_VOICE_ID).strip()

    for index, scene in enumerate(scenes, start=1):
        if not isinstance(scene, dict):
            raise VoiceoverError(f"Scene {index} is not in the expected format.")

        order = scene.get("order", index)
        output_path = AUDIO_OUTPUT_DIR / f"scene_{order}.mp3"
        narration = scene.get("narration", "")

        logger.info("Generating voiceover for scene %s...", order)
        try:
            spoken_text = generate_voice_clip(narration, api_key, voice_id, output_path)
        except VoiceoverError as e:
            raise VoiceoverError(f"Voiceover failed on scene {order}: {e}") from e

        duration = get_audio_duration_seconds(output_path)
        if duration is None:
            duration = _estimate_duration_seconds(spoken_text)
            logger.info("  Using estimated duration for scene %s: %ss", order, duration)

        scene["audio_path"] = str(output_path)
        scene["actual_duration_seconds"] = duration
        logger.info("  Saved: %s (duration: %ss)", output_path, duration)

    return script


if __name__ == "__main__":
    with open("script_with_footage.json") as f:
        script_data = json.load(f)

    script_with_audio = generate_voiceovers_for_script(script_data)

    with open("script_with_audio.json", "w") as f:
        json.dump(script_with_audio, f, indent=2)

    logger.info("Saved to script_with_audio.json")
