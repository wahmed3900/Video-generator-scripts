"""
generate_scene_images.py

Step 2 of the pipeline (replaces Pexels stock footage).
For each scene, generates a cinematic 9:16 AI image with Gemini 3.1 Flash Image,
using the GEMINI_API_KEY you already have.

Each scene gets scene["ai_image"] = local file path (or None on failure,
so the old Pexels clip can be used as a fallback).
"""

from pathlib import Path
from google import genai
from google.genai import types

IMAGE_MODEL = "gemini-3.1-flash-image"  # replaced Imagen 4 (shut down Aug 2026)
IMAGES_DIR = Path("images")

# Added to every prompt so all scenes share one premium, consistent look
STYLE = (
    "cinematic vertical shot, dramatic lighting, shallow depth of field, "
    "rich color grading, ultra detailed, sharp focus, 35mm film look, "
    "no text, no watermark"
)


def generate_image(client: genai.Client, prompt: str, output_path: Path) -> Path | None:
    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=f"{prompt}, {STYLE}",
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="9:16"),
            ),
        )
        image_bytes = next(
            part.inline_data.data
            for part in response.candidates[0].content.parts
            if part.inline_data
        )
        output_path.write_bytes(image_bytes)
        return output_path
    except Exception as e:
        print(f"  Image generation failed: {e}")
        return None


def attach_ai_images_to_script(script: dict, api_key: str) -> dict:
    client = genai.Client(api_key=api_key)
    IMAGES_DIR.mkdir(exist_ok=True)

    scenes = list(script["scenes"])
    if script.get("cta"):
        scenes.append(script["cta"])

    for i, scene in enumerate(scenes, start=1):
        print(f"Scene {i}: generating AI image...")
        path = generate_image(client, scene["visual_description"], IMAGES_DIR / f"scene_{i}.png")
        scene["ai_image"] = str(path) if path else None

    return script
