"""
generate_voiceover.py

Step 3 of the video-generator pipeline. Takes script_with_footage.json
(produced by fetch_stock_footage.py) and generates a voiceover audio file
for each scene's narration using the ElevenLabs API.

Usage:
    python generate_voiceover.py

Requires:
    pip install requests python-dotenv
    An ELEVENLABS_API_KEY environment variable (or .env entry)
    script_with_footage.json in the same directory (produced by step 2)

Output:
    - One .mp3 file per scene, saved to ./audio/scene_<order>.mp3
    - script_with_audio.json — same structure as input, plus an
      "audio_path" and "actual_duration_seconds" field per scene
"""

import os
import json
import requests
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional; environment variables can be set another way

ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

# A default ElevenLabs voice ID (Adam — a commonly used, natural-sounding
# voice). Swap this for any voice ID from your ElevenLabs account.
DEFAULT_VOICE_ID = "pNInz6obpgDQGcFmaJgB"

AUDIO_OUTPUT_DIR = Path("audio")


def generate_voice_clip(text: str, api_key: str, voice_id: str, output_path: Path) -> None:
    """
    Calls ElevenLabs TTS for a single piece of narration text and saves
    the resulting audio to output_path.

    Args:
        text: The narration text to speak.
        api_key: Your ElevenLabs API key.
        voice_id: Which ElevenLabs voice to use.
        output_path: Where to save the resulting .mp3 file.
    """
    url = ELEVENLABS_TTS_URL.format(voice_id=voice_id)
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if not response.ok:
        print(f"ElevenLabs error response: {response.status_code} - {response.text}")
    response.raise_for_status()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(response.content)


def get_audio_duration_seconds(file_path: Path) -> float:
    """
    Returns the duration of an audio file in seconds using mutagen,
    so the assembly step can sync visuals to actual narration length
    (not just the LLM's estimate).
    """
    try:
        from mutagen.mp3 import MP3
        audio = MP3(file_path)
        return round(audio.info.length, 2)
    except ImportError:
        # mutagen not installed — fall back to the script's estimate
        return None


def generate_voiceovers_for_script(script: dict, api_key: str, voice_id: str = DEFAULT_VOICE_ID) -> dict:
    """
    For each scene in the script, generates a voiceover clip and attaches
    its file path and actual duration.
    """
    for scene in script["scenes"]:
        order = scene["order"]
        output_path = AUDIO_OUTPUT_DIR / f"scene_{order}.mp3"

        print(f"Generating voiceover for scene {order}...")
        generate_voice_clip(scene["narration"], api_key, voice_id, output_path)

        scene["audio_path"] = str(output_path)
        scene["actual_duration_seconds"] = get_audio_duration_seconds(output_path)

        print(f"  Saved: {output_path} (actual duration: {scene['actual_duration_seconds']}s)")

    return script


if __name__ == "__main__":
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise EnvironmentError("Set ELEVENLABS_API_KEY before running this script.")

    with open("script_with_footage.json") as f:
        script = json.load(f)

    script_with_audio = generate_voiceovers_for_script(script, api_key)

    with open("script_with_audio.json", "w") as f:
        json.dump(script_with_audio, f, indent=2)

    print("\nSaved to script_with_audio.json")