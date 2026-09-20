"""
generate_video_script.py

Calls the Anthropic API to turn a topic into a structured, hook-optimized
short-form video script (JSON: hook + scenes with narration + visual
descriptions). This is step 1 of the video-generator pipeline — it feeds
the output into your TTS (voiceover) and stock-footage/video-assembly steps.

Usage:
    python generate_video_script.py

Requires:
    pip install anthropic google-genai
    An ANTHROPIC_API_KEY environment variable set with your API key.
    (Optional, for the Gemini fallback) A GEMINI_API_KEY environment variable.
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
    from google import genai
except ImportError:
    genai = None  # google-genai is optional; only needed for the Gemini fallback

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

MODEL = "claude-opus-4-1"  # Fast + strong writing quality for this use case
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

3. RETENTION CHECKPOINTS: Viewers are most likely to drop off at three
   points — around the 3-second mark (if the hook doesn't pay off fast
   enough), the midpoint (when momentum sags), and just before the ending
   (once they think they've "gotten the point"). At each of these points,
   insert a pattern interrupt: a visual change, a direct question, a
   surprising reveal, or a tone shift. Flag which scenes sit at these
   checkpoints.

4. ENDING: Close the BODY with a payoff, punchline, or resolution that
   rewards watching to the end — never trail off or summarize what was
   already said. Do NOT put a call-to-action in the body's final scene;
   that belongs in the separate CTA scene described below.

5. For EACH body scene, output:
   - narration: the exact words to be spoken (natural spoken language, no
     stage directions)
   - visual_description: a short phrase describing what should appear on
     screen (concrete and visual, e.g. "closeup of hands typing on laptop"
     — not abstract concepts)
   - duration_seconds: estimated spoken length
   - retention_risk: "low", "medium", or "high" — how likely a viewer is to
     drop off during THIS scene specifically (be honest; not every scene
     should be "low")
   - retention_note: one short sentence on why that risk level applies here,
     and what (if anything) in the scene is designed to counter it

6. CTA SCENE: After the body's ending, write ONE separate final scene whose
   sole purpose is maximizing rewatch/follow/comment behavior — not
   restating the video's content. Pick whichever fits the topic best:
   a direct ask to follow for part 2, a question that invites comments,
   a "watch it again to catch X" rewatch hook, or a fast-paced recap in
   under 2 seconds that loops naturally back into the hook. Output:
   - narration
   - visual_description
   - duration_seconds
   - cta_type: one of "follow", "comment_bait", "rewatch_loop", "link_in_bio"

Return ONLY valid JSON in this exact structure, no other text:

{{
  "hook_strength_notes": "one sentence explaining why this hook should work",
  "scenes": [
    {{
      "order": 1,
      "narration": "...",
      "visual_description": "...",
      "duration_seconds": 3,
      "retention_risk": "low",
      "retention_note": "..."
    }}
  ],
  "cta_scene": {{
    "narration": "...",
    "visual_description": "...",
    "duration_seconds": 3,
    "cta_type": "rewatch_loop"
  }},
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
        first_block = response.content[0]
        block_text = getattr(first_block, "text", None)
        if block_text is None:
            raise RuntimeError(
                f"Unexpected Claude response block type: {type(first_block).__name__} "
                "(expected a text block)"
            )
        raw_text = block_text.strip()
    except Exception as e:
        anthropic_error = e
        print(f"Anthropic call failed ({e}); falling back to Gemini...")

    # Fall back to Gemini if Anthropic failed and google-genai is available
    if raw_text is None:
        if genai is None:
            raise RuntimeError(
                "Anthropic call failed and google-genai is not installed. "
                "Run: pip install google-genai"
            ) from anthropic_error

        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            raise RuntimeError(
                "Anthropic call failed and GEMINI_API_KEY is not set for fallback."
            ) from anthropic_error

        gemini_client = genai.Client(api_key=gemini_key)
        gemini_response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        raw_text = gemini_response.text.strip()

    # Defensive cleanup in case the model wraps output in markdown fences
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON. Raw response:\n{raw_text}") from e

    # Fold the CTA scene into the main scenes list so it flows through the
    # rest of the pipeline (stock footage, voiceover, video assembly)
    # exactly like any other scene — those steps only know how to iterate
    # script["scenes"], so a separate top-level cta_scene field would
    # otherwise be silently dropped before it ever reaches the final video.
    cta = data.pop("cta_scene", None)
    if cta:
        cta = dict(cta)
        cta["order"] = len(data.get("scenes", [])) + 1
        cta.setdefault("retention_risk", "n/a")
        cta.setdefault("retention_note", f"CTA scene ({cta.get('cta_type', 'cta')})")
        data.setdefault("scenes", []).append(cta)

    # Recompute total duration from the actual scene durations rather than
    # trusting the model's arithmetic — it can drift, especially now that
    # the CTA scene is folded in after the fact.
    data["total_duration_seconds"] = sum(
        s.get("duration_seconds", 0) for s in data.get("scenes", [])
    )

    return data


if __name__ == "__main__":
    # --- Quick manual test ---
    topic = "Why most stock apps hide their best features behind a paywall"

    script = generate_script(topic, duration_seconds=20, tone="energetic and casual")

    print("\n=== HOOK NOTES ===")
    print(script["hook_strength_notes"])

    print("\n=== SCENES ===")
    for scene in script["scenes"]:
        print(f"\nScene {scene['order']} ({scene['duration_seconds']}s) — retention risk: {scene.get('retention_risk', 'n/a')}")
        print(f"  Narration: {scene['narration']}")
        print(f"  Visual:    {scene['visual_description']}")
        if scene.get('retention_note'):
            print(f"  Why:       {scene['retention_note']}")

    if script.get("cta_scene"):
        cta = script["cta_scene"]
        print(f"\n=== CTA SCENE ({cta.get('cta_type', 'n/a')}, {cta.get('duration_seconds', '?')}s) ===")
        print(f"  Narration: {cta['narration']}")
        print(f"  Visual:    {cta['visual_description']}")

    print(f"\nTotal duration: {script['total_duration_seconds']}s")

    # Save to a file so the next pipeline step (TTS / video assembly) can read it
    with open("script_output.json", "w") as f:
        json.dump(script, f, indent=2)
    print("\nSaved to script_output.json")
