"""
assemble_video.py

Step 4 (final step) of the video-generator pipeline. Takes
script_with_audio.json (produced by generate_voiceover.py) and:
  1. Downloads each scene's stock video clip
  2. Trims/loops each clip to match its actual voiceover duration
  3. Burns in captions (the narration text) onto each clip
  4. Concatenates all scenes together
  5. Merges the combined video with the combined voiceover audio

Usage:
    python assemble_video.py

Requires:
    - FFmpeg installed and available on your PATH
      (macOS: brew install ffmpeg)
    - pip install requests
    - script_with_audio.json in the same directory (produced by step 3)
    - The audio/ folder from step 3 (voiceover .mp3 files)

Output:
    - final_video.mp4
"""

import json
import subprocess
import textwrap
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def run_ffmpeg(cmd: list[str], step_name: str) -> None:
    """Runs an FFmpeg command and raises with the real stderr output on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg error ({step_name}):\n{result.stderr}")
        raise RuntimeError(f"FFmpeg failed during: {step_name}")

RAW_CLIPS_DIR = Path("raw_clips")
PROCESSED_CLIPS_DIR = Path("processed_clips")
FINAL_OUTPUT = Path("final_video.mp4")

# Output video settings — 9:16 vertical for TikTok/Reels/Shorts
OUTPUT_WIDTH = 1080
OUTPUT_HEIGHT = 1920


def download_clip(url: str, output_path: Path) -> None:
    """Downloads a stock video clip from its Pexels URL."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def create_caption_image(text: str, width: int, height: int, output_path: Path) -> None:
    """
    Renders the caption text onto a transparent PNG the same size as the
    video frame, using Pillow instead of FFmpeg's drawtext filter (which
    requires a libfreetype-enabled FFmpeg build that isn't always available,
    e.g. on some Homebrew installs).
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_size = 56
    font = None
    for font_path in [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # common on Linux
    ]:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except (OSError, IOError):
            continue
    if font is None:
        font = ImageFont.load_default()

    wrapped_lines = textwrap.fill(text, width=28).split("\n")
    line_height = font_size + 14
    total_text_height = line_height * len(wrapped_lines)
    y = height - 350 - total_text_height // 2

    for line in wrapped_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = (width - text_w) // 2

        # Semi-transparent background box behind the text
        draw.rectangle(
            [x - 20, y - 8, x + text_w + 20, y + line_height - 6],
            fill=(0, 0, 0, 100),
        )
        # White text with black outline (stroke) for readability
        draw.text((x, y), line, font=font, fill="white", stroke_width=3, stroke_fill="black")
        y += line_height

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)


def process_scene_clip(raw_clip_path: Path, output_path: Path, duration: float, caption_text: str) -> None:
    """
    Uses FFmpeg to:
      - Crop/scale the clip to 9:16 vertical
      - Trim or loop it to match the target duration
      - Overlay a pre-rendered caption image (from create_caption_image)

    Args:
        raw_clip_path: Path to the downloaded stock clip.
        output_path: Where to save the processed clip.
        duration: Target duration in seconds (from actual voiceover length).
        caption_text: The narration text to overlay as a caption.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    caption_path = output_path.parent / f"{output_path.stem}_caption.png"
    create_caption_image(caption_text, OUTPUT_WIDTH, OUTPUT_HEIGHT, caption_path)

    filter_complex = (
        f"[0:v]scale={OUTPUT_WIDTH}:{OUTPUT_HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={OUTPUT_WIDTH}:{OUTPUT_HEIGHT}[bg];"
        f"[bg][1:v]overlay=0:0[out]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",       # loop the input if it's shorter than target duration
        "-i", str(raw_clip_path),
        "-i", str(caption_path),
        "-t", str(duration),        # trim to exact duration
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-an",                      # strip original clip audio (we use TTS voiceover instead)
        str(output_path),
    ]

    run_ffmpeg(cmd, f"processing {raw_clip_path}")


def concatenate_clips(clip_paths: list[Path], output_path: Path) -> None:
    """Concatenates processed clips into one silent video track."""
    concat_list_path = Path("concat_list.txt")
    with open(concat_list_path, "w") as f:
        for clip_path in clip_paths:
            f.write(f"file '{clip_path.resolve()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list_path),
        "-c", "copy",
        str(output_path),
    ]
    run_ffmpeg(cmd, "concatenating video clips")
    concat_list_path.unlink()


def concatenate_audio(audio_paths: list[Path], output_path: Path) -> None:
    """Concatenates all scene voiceover clips into one audio track."""
    concat_list_path = Path("audio_concat_list.txt")
    with open(concat_list_path, "w") as f:
        for audio_path in audio_paths:
            f.write(f"file '{audio_path.resolve()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list_path),
        "-c", "copy",
        str(output_path),
    ]
    run_ffmpeg(cmd, "concatenating audio clips")
    concat_list_path.unlink()


def merge_video_and_audio(video_path: Path, audio_path: Path, output_path: Path) -> None:
    """Merges the silent concatenated video with the concatenated voiceover track."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_path),
    ]
    run_ffmpeg(cmd, "merging video and audio")


def assemble_video(script: dict) -> Path:
    """
    Runs the full assembly pipeline: download clips, process each scene,
    concatenate video, concatenate audio, merge the two.

    Returns:
        Path to the final .mp4 file.
    """
    processed_clip_paths = []
    audio_paths = []

    for scene in script["scenes"]:
        order = scene["order"]
        stock_clip = scene.get("stock_clip")
        duration = scene.get("actual_duration_seconds") or scene["duration_seconds"]

        if not stock_clip:
            print(f"Scene {order}: no stock clip available, skipping (needs manual fallback)")
            continue

        raw_path = RAW_CLIPS_DIR / f"scene_{order}.mp4"
        processed_path = PROCESSED_CLIPS_DIR / f"scene_{order}.mp4"

        print(f"Scene {order}: downloading clip...")
        download_clip(stock_clip["download_url"], raw_path)

        print(f"Scene {order}: processing (duration={duration}s)...")
        process_scene_clip(raw_path, processed_path, duration, scene["narration"])

        processed_clip_paths.append(processed_path)
        audio_paths.append(Path(scene["audio_path"]))

    if not processed_clip_paths:
        raise RuntimeError("No scenes had usable stock clips — nothing to assemble.")

    silent_video_path = Path("combined_silent.mp4")
    combined_audio_path = Path("combined_audio.mp3")

    print("Concatenating video clips...")
    concatenate_clips(processed_clip_paths, silent_video_path)

    print("Concatenating audio clips...")
    concatenate_audio(audio_paths, combined_audio_path)

    print("Merging video and audio...")
    merge_video_and_audio(silent_video_path, combined_audio_path, FINAL_OUTPUT)

    # Cleanup intermediate files
    silent_video_path.unlink(missing_ok=True)
    combined_audio_path.unlink(missing_ok=True)

    return FINAL_OUTPUT


if __name__ == "__main__":
    with open("script_with_audio.json") as f:
        script = json.load(f)

    final_path = assemble_video(script)
    print(f"\nDone! Final video saved to: {final_path.resolve()}")