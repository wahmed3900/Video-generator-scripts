
"""
fetch_stock_footage.py

Step 2 of the video-generator pipeline. Takes the script_output.json
produced by generate_video_script.py and, for each scene, searches Pexels
for a matching stock video clip using the scene's visual_description as
the search query.

Usage:
    python fetch_stock_footage.py

Requires:
    pip install requests
    A PEXELS_API_KEY environment variable (free at https://www.pexels.com/api/)
    script_output.json in the same directory (produced by step 1)
"""


import os
import json
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional; environment variables can be set another way

PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"
MIN_DURATION_SECONDS = 3   # skip clips shorter than this
PREFERRED_ORIENTATION = "landscape"  # or "portrait" for TikTok/Reels-style output


def search_stock_clip(query: str, api_key: str, min_duration: int = MIN_DURATION_SECONDS) -> dict | None:
    """
    Searches Pexels for a video clip matching the query.

    Args:
        query: Search keywords (typically a scene's visual_description).
        api_key: Your Pexels API key.
        min_duration: Minimum acceptable clip length in seconds.

    Returns:
        A dict with clip info (id, url, duration, download_url) or None
        if no suitable clip was found.
    """
    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "per_page": 5,
        "orientation": PREFERRED_ORIENTATION,
    }

    response = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    videos = data.get("videos", [])
    if not videos:
        return None

    # Pick the first video that meets the minimum duration
    for video in videos:
        if video["duration"] >= min_duration:
            # Pick a reasonably-sized file (avoid 4K when not needed)
            files = sorted(video["video_files"], key=lambda f: f.get("width", 0))
            best_file = next(
                (f for f in files if f.get("width", 0) >= 720),
                files[-1] if files else None,
            )
            if not best_file:
                continue

            return {
                "pexels_id": video["id"],
                "duration": video["duration"],
                "preview_url": video["url"],
                "download_url": best_file["link"],
                "width": best_file.get("width"),
                "height": best_file.get("height"),
            }

    # Nothing met the duration threshold — fall back to the first result
    fallback = videos[0]
    files = sorted(fallback["video_files"], key=lambda f: f.get("width", 0))
    best_file = files[-1] if files else None
    if not best_file:
        return None

    return {
        "pexels_id": fallback["id"],
        "duration": fallback["duration"],
        "preview_url": fallback["url"],
        "download_url": best_file["link"],
        "width": best_file.get("width"),
        "height": best_file.get("height"),
    }


def attach_footage_to_script(script: dict, api_key: str) -> dict:
    """
    For each scene in the script, searches for and attaches a matching
    stock video clip under scene["stock_clip"].

    Scenes with no match get stock_clip = None so the caller can decide
    how to handle gaps (retry with a broader query, use a fallback image, etc).
    """
    for scene in script["scenes"]:
        query = scene["visual_description"]
        clip = search_stock_clip(query, api_key)
        scene["stock_clip"] = clip

        if clip:
            print(f"Scene {scene['order']}: found clip for '{query}' ({clip['duration']}s)")
        else:
            print(f"Scene {scene['order']}: NO MATCH for '{query}' — needs fallback")

    return script


if __name__ == "__main__":
    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        raise EnvironmentError("Set PEXELS_API_KEY before running this script.")

    with open("script_output.json") as f:
        script = json.load(f)

    script_with_footage = attach_footage_to_script(script, api_key)

    with open("script_with_footage.json", "w") as f:
        json.dump(script_with_footage, f, indent=2)

    print("\nSaved to script_with_footage.json")