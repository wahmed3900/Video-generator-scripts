"""
generate_marketing.py

Step 4 of the video-generator pipeline. Takes script_with_footage.json
produced by fetch_stock_footage.py and generates platform-specific
marketing copy (YouTube, TikTok, Instagram, X, email) using Gemini.

Usage:
    python generate_marketing.py

Requires:
    pip install google-genai
    A GEMINI_API_KEY environment variable (free at https://aistudio.google.com/apikey)
    script_with_footage.json in the same directory (produced by step 2)

Output:
    script_with_marketing.json — the original script plus a "marketing" key
    containing copy for each platform.
"""


import os
import re
import json

from google import genai

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional; environment variables can be set another way

INPUT_FILE = "script_with_footage.json"
OUTPUT_FILE = "script_with_marketing.json"
MODEL_NAME = "gemini-2.5-flash"  # swap for a newer model as they're released


PROMPT_TEMPLATE = """You are a senior social media marketer. Below is the script for a short video.

Your job: write platform-specific marketing copy that will make people stop scrolling
and watch. Match the tone of the script. Be concrete, punchy, and avoid generic filler
like "In today's world" or "Unlock the secrets."

Return ONLY valid JSON, no markdown fences, no commentary. Use exactly this shape:

{{
  "youtube": {{
    "title": "60 chars max, keyword-rich, curiosity-driven",
    "description": "2-3 short paragraphs, include a hook, a summary, and a call to action",
    "tags": ["8-12 lowercase tags, no # symbol"],
    "thumbnail_text": "3-5 words, all caps, high contrast"
  }},
  "tiktok": {{
    "hook": "first 3 seconds of on-screen text or voiceover",
    "caption": "under 150 chars",
    "hashtags": ["5-8 tags, each starting with #"]
  }},
  "instagram": {{
    "caption": "under 300 chars, line breaks allowed",
    "hashtags": ["8-15 tags, each starting with #"]
  }},
  "x": {{
    "post": "under 280 chars, no hashtag spam, one strong idea"
  }},
  "email": {{
    "subject": "under 60 chars, no clickbait",
    "preview": "under 90 chars",
    "body": "3-5 short paragraphs with a single clear CTA"
  }},
  "linkedin": {{
    "post": "professional tone, 3-5 short paragraphs, one takeaway"
  }}
}}

SCRIPT:

Title: {title}
Total scenes: {scene_count}

{scenes}
"""


def _format_scenes(script: dict) -> str:
    """Turns the script's scenes into a readable block for the prompt."""
    lines = []
    for scene in script.get("scenes", []):
        order = scene.get("order", "?")
        narration = scene.get("narration", "").strip()
        visual = scene.get("visual_description", "").strip()
        lines.append(f"Scene {order}")
        lines.append(f"  Narration: {narration}")
        if visual:
            lines.append(f"  Visual: {visual}")
        lines.append("")
    return "\n".join(lines)


def _strip_json_fences(text: str) -> str:
    """
    Gemini sometimes wraps JSON in ```json ... ``` fences. Strip them so
    json.loads() doesn't choke.
    """
    text = text.strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence:
        return fence.group(1)
    return text


def generate_marketing_copy(script: dict, api_key: str) -> dict:
    """
    Sends the script to Gemini and returns a dict of marketing copy keyed
    by platform. Raises RuntimeError if the response can't be parsed.
    """
    client = genai.Client(api_key=api_key)

    prompt = PROMPT_TEMPLATE.format(
        title=script.get("title", "Untitled"),
        scene_count=len(script.get("scenes", [])),
        scenes=_format_scenes(script),
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    raw = response.text or ""
    cleaned = _strip_json_fences(raw)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Gemini returned non-JSON output. First 500 chars:\n{raw[:500]}"
        ) from e


def attach_marketing_to_script(script: dict, api_key: str) -> dict:
    """
    Adds a "marketing" key to the script containing platform copy.
    If generation fails, marketing is set to None so the caller can decide
    how to handle it without losing the rest of the script.
    """
    print("Generating marketing copy with Gemini...")
    try:
        marketing = generate_marketing_copy(script, api_key)
        script["marketing"] = marketing
        platforms = ", ".join(marketing.keys())
        print(f"  Generated copy for: {platforms}")
    except Exception as e:
        print(f"  FAILED: {e}")
        script["marketing"] = None

    return script


if __name__ == "__main__":
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("Set GEMINI_API_KEY before running this script.")

    with open(INPUT_FILE) as f:
        script = json.load(f)

    script_with_marketing = attach_marketing_to_script(script, api_key)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(script_with_marketing, f, indent=2)

    print(f"\nSaved to {OUTPUT_FILE}")
