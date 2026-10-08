"""
niche_research.py

Pulls the top-performing recent Shorts for a niche from the YouTube Data API,
so the script writer can study what's already winning.

    examples = get_niche_examples("personal finance", youtube_key)
    # -> [{"title": "...", "views": 1200000}, ...]

Never raises: on any problem it returns [] and the script is written normally.
Results are cached for 24 hours per niche, because each search uses
100 of your 10,000 free daily YouTube API units.
"""

import time
from datetime import datetime, timedelta, timezone

import requests

API = "https://www.googleapis.com/youtube/v3"
CACHE_HOURS = 24
_cache: dict[str, tuple[float, list]] = {}


def get_niche_examples(niche: str, api_key: str | None, limit: int = 10) -> list[dict]:
    niche = (niche or "").strip().lower()
    if not niche or not api_key:
        return []

    cached = _cache.get(niche)
    if cached and time.time() - cached[0] < CACHE_HOURS * 3600:
        return cached[1]

    try:
        since = (datetime.now(timezone.utc) - timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # 1. Find popular short videos in this niche from the last 60 days
        search = requests.get(f"{API}/search", timeout=15, params={
            "part": "snippet",
            "q": f"{niche} #shorts",
            "type": "video",
            "videoDuration": "short",
            "order": "viewCount",
            "publishedAfter": since,
            "maxResults": 25,
            "relevanceLanguage": "en",
            "key": api_key,
        })
        search.raise_for_status()
        ids = [item["id"]["videoId"] for item in search.json().get("items", [])]
        if not ids:
            return []

        # 2. Get their real view counts (costs only 1 unit)
        stats = requests.get(f"{API}/videos", timeout=15, params={
            "part": "snippet,statistics",
            "id": ",".join(ids),
            "key": api_key,
        })
        stats.raise_for_status()

        examples = [
            {
                "title": v["snippet"]["title"],
                "views": int(v["statistics"].get("viewCount", 0)),
            }
            for v in stats.json().get("items", [])
        ]
        examples.sort(key=lambda e: e["views"], reverse=True)
        examples = examples[:limit]

        _cache[niche] = (time.time(), examples)
        return examples

    except Exception as e:
        print(f"Niche research failed for '{niche}': {e}")
        return []


def format_examples_for_prompt(niche: str, examples: list[dict]) -> str:
    """Turns the examples into a block of text to add to the script prompt."""
    if not examples:
        return ""
    lines = "\n".join(f'- "{e["title"]}" ({e["views"]:,} views)' for e in examples)
    return (
        f"\n\nNICHE: {niche}\n"
        f"These are the top-performing recent Shorts in this niche:\n{lines}\n\n"
        "Study what makes them work: the hook style, the promise, the wording "
        "this audience responds to. Write an ORIGINAL script that uses the same "
        "proven patterns. Do not copy any title or idea directly. "
        "The first sentence must be a strong hook that stops the scroll."
    )
