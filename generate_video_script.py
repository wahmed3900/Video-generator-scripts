"""
generate_video_script.py

Calls the Anthropic API to turn a topic into a structured, hook-optimized
short-form video script (JSON: hook + scenes with narration + visual
descriptions). This is step 1 of the video-generator pipeline — it feeds
the output into your TTS (voiceover) and stock-footage/video-assembly steps.

Usage:
    python generate_video_script.py

Requires:
    pip install anthropic
    An ANTHROPIC_API_KEY environment variable set with your API key.
"""

import os
import json
import anthropic

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional; environment variables can be set another way

try:
    import google.generativeai as genai
except ImportError:
    genai = None  # google-generativeai is optional; only needed for the Gemini fallback

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

MODEL = "claude-sonnet-4-6"  # Fast + strong writing quality for this use case
MAX_TOKENS = 1500
GEMINI_MODEL = "gemini-3.6-flash"  # used only if ANTHROPIC_API_KEY is missing/invalid

PROMPT_TEMPLATE = """You are a short-form video scriptwriter specializing in scroll-stopping,
high-retention content for platforms like TikTok, Reels, and YouTube Shorts.

TOPIC: {topic}
TARGET LENGTH: {duration} seconds (aim for ~2.5 words per second of narration)
TONE: {tone}

Write a script following these rules:

1. HOOK (first line only): Open with one of these techniques — a surprising
   stat, a bold claim, a direct question to the viewer, or a "most people
   get this wrong" framing. It must work even with no visual context, since
   many viewers watch the first second before deciding to keep watching.

2. BODY: Break the content into short scenes. Each scene should be a single
   idea, sentence, or fact — no run-on explanations. Aim for scenes of 2-4
   seconds of narration each.

3. ENDING: Close with a payoff, punchline, or call-to-action that rewards
   watching to the end — never trail off or summarize what was already said.

4. For EACH scene, output:
   - narration: the exact words to be spoken (natural spoken language, no
     stage directions)
   - visual_description: a short phrase describing what should appear on
     screen (concrete and visual, e.g. "closeup of hands typing on laptop"
     — not abstract concepts)
   - duration_seconds: estimated spoken length

Return ONLY valid JSON in this exact structure, no other text:

{{
  "hook_strength_notes": "one sentence explaining why this hook should work",
  "scenes": [
    {{
      "order": 1,
      "narration": "...",
      "visual_description": "...",
      "duration_seconds": 3
    }}
  ],
  "total_duration_seconds": 45
}}
"""


def generate_script(topic: str, duration_seconds: int = 30, tone: str = "punchy and direct") -> dict:
    """
    Calls Claude to generate a structured video script.

    Args:
        topic: What the video should be about (e.g. "3 tips for HVAC maintenance").
        duration_seconds: Target total video length.
        tone: Optional tone guidance for the writing style.

    Returns:
        A dict matching the JSON structure described in the prompt
        (hook_strength_notes, scenes[], total_duration_seconds).

    Raises:
        ValueError: if the model's response isn't valid JSON.
    """
    prompt = PROMPT_TEMPLATE.format(topic=topic, duration=duration_seconds, tone=tone)

    raw_text = None
    anthropic_error = None

    # Try Anthropic (Claude) first
    try:
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = response.content[0].text.strip()
    except Exception as e:
        anthropic_error = e
        print(f"Anthropic call failed ({e}); falling back to Gemini...")

    # Fall back to Gemini if Anthropic failed and google-generativeai is available
    if raw_text is None:
        if genai is None:
            raise RuntimeError(
                "Anthropic call failed and google-generativeai is not installed. "
                "Run: pip install google-generativeai"
            ) from anthropic_error

        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            raise RuntimeError(
                "Anthropic call failed and GEMINI_API_KEY is not set for fallback."
            ) from anthropic_error

        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel(GEMINI_MODEL)
        gemini_response = model.generate_content(prompt)
        raw_text = gemini_response.text.strip()

    # Defensive cleanup in case the model wraps output in markdown fences
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON. Raw response:\n{raw_text}") from e


if __name__ == "__main__":
    # --- Quick manual test ---
    topic = "Why most stock apps hide their best features behind a paywall"

    script = generate_script(topic, duration_seconds=20, tone="energetic and casual")

    print("\n=== HOOK NOTES ===")
    print(script["hook_strength_notes"])

    print("\n=== SCENES ===")
    for scene in script["scenes"]:
        print(f"\nScene {scene['order']} ({scene['duration_seconds']}s)")
        print(f"  Narration: {scene['narration']}")
        print(f"  Visual:    {scene['visual_description']}")

    print(f"\nTotal duration: {script['total_duration_seconds']}s")

    # Save to a file so the next pipeline step (TTS / video assembly) can read it
    with open("script_output.json", "w") as f:
        json.dump(script, f, indent=2)
    print("\nSaved to script_output.json")