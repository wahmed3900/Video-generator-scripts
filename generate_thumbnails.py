"""
generate_thumbnails.py

Makes 3 YouTube thumbnail variants (1280x720) for a video:
  1. Gemini writes 3 short, punchy headlines (2-4 words) from the hook.
  2. Gemini 3.1 Flash Image draws a high-contrast background for each,
     leaving the left side clear for text.
  3. Pillow adds the headline in big bold text (sharper than AI-drawn text).

Usage in the pipeline:
    script = attach_thumbnails_to_script(script, gemini_key)
    # script["thumbnails"] -> ["thumbnails/thumb_1.jpg", ...]
"""

import json
from pathlib import Path
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont

TEXT_MODEL = "gemini-flash-latest"
IMAGE_MODEL = "gemini-3.1-flash-image"
OUT_DIR = Path("thumbnails")
SIZE = (1280, 720)

STYLES = [
    "expressive person with a shocked face on the right side, bright saturated colors",
    "dramatic close-up object on the right side, dark moody background with one strong color glow",
    "bold clean scene on the right side, high contrast, vivid complementary colors",
]

TEXT_COLORS = ["#FFE600", "#FFFFFF", "#00F0FF"]

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]


def make_headlines(client: genai.Client, topic_hook: str) -> list[str]:
    prompt = (
        "Write 3 different YouTube thumbnail headlines for this video hook. "
        "Each must be 2 to 4 words, ALL CAPS, curiosity-driven, no punctuation except ? or !. "
        'Return ONLY a JSON array of 3 strings, e.g. ["STOP DOING THIS", "IT\'S A TRAP", "I WAS WRONG"].\n\n'
        f"Hook: {topic_hook}"
    )
    response = client.models.generate_content(model=TEXT_MODEL, contents=prompt)
    text = response.text.replace("```json", "").replace("```", "").strip()
    headlines = json.loads(text)
    return [h.upper() for h in headlines[:3]]


def make_background(client: genai.Client, subject: str, style: str) -> Image.Image:
    prompt = (
        f"YouTube thumbnail background about: {subject}. {style}. "
        "Keep the LEFT 45% of the image simple and uncluttered for text. "
        "Cinematic lighting, sharp focus, ultra detailed. No text, no letters, no watermark."
    )
    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="16:9"),
        ),
    )
    data = next(p.inline_data.data for p in response.candidates[0].content.parts if p.inline_data)
    tmp = OUT_DIR / "_bg.png"
    tmp.write_bytes(data)
    return Image.open(tmp).convert("RGB").resize(SIZE)


def load_font(size: int) -> ImageFont.ImageFont:
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def add_headline(img: Image.Image, headline: str, color: str) -> Image.Image:
    # Dark gradient on the left so text always pops
    overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for x in range(int(SIZE[0] * 0.6)):
        alpha = int(170 * (1 - x / (SIZE[0] * 0.6)))
        od.line([(x, 0), (x, SIZE[1])], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)

    draw = ImageDraw.Draw(img)
    words = headline.split()
    lines = [" ".join(words[i:i + 2]) for i in range(0, len(words), 2)]  # 2 words per line

    font_size = 150
    font = load_font(font_size)
    max_width = SIZE[0] * 0.5
    while font_size > 60 and max(draw.textbbox((0, 0), l, font=font)[2] for l in lines) > max_width:
        font_size -= 8
        font = load_font(font_size)

    line_h = font_size + 10
    y = (SIZE[1] - line_h * len(lines)) // 2
    for line in lines:
        draw.text((60, y), line, font=font, fill=color, stroke_width=10, stroke_fill="black")
        y += line_h

    return img.convert("RGB")


def attach_thumbnails_to_script(script: dict, api_key: str) -> dict:
    """Never raises: on failure sets script["thumbnails"] = [] so the pipeline continues."""
    try:
        client = genai.Client(api_key=api_key)
        OUT_DIR.mkdir(exist_ok=True)

        first_scene = script["scenes"][0]
        hook = first_scene["narration"]
        subject = first_scene["visual_description"]

        headlines = make_headlines(client, hook)
        paths = []
        for i, (headline, style, color) in enumerate(zip(headlines, STYLES, TEXT_COLORS), start=1):
            print(f"Thumbnail {i}: {headline}")
            bg = make_background(client, subject, style)
            thumb = add_headline(bg, headline, color)
            path = OUT_DIR / f"thumb_{i}.jpg"
            thumb.save(path, "JPEG", quality=92)
            paths.append(str(path))

        script["thumbnails"] = paths
    except Exception as e:
        print(f"Thumbnail generation failed: {e}")
        script["thumbnails"] = []
    return script
