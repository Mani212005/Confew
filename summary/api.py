"""API-facing processing helpers for MVP endpoint behavior."""

from __future__ import annotations

from tempfile import NamedTemporaryFile

from summary.llm_processing import distill_content
from summary.text_processing import clean_text
from summary.utils.validators import validate_process_payload
from summary.visualization import generate_infographic
from summary.youtube_processing import extract_transcript as _extract_transcript

# Expose symbol for monkeypatching in tests.
extract_transcript = _extract_transcript


def process_youtube(payload: dict) -> dict:
    """Process a YouTube URL payload into a compact API response shape."""
    url = validate_process_payload(payload)
    transcript = extract_transcript(url)
    cleaned = clean_text(transcript)
    distilled = distill_content(cleaned)

    with NamedTemporaryFile(suffix=".png", prefix="summary_api_infographic_", delete=False) as tmp:
        infographic_url = generate_infographic(distilled, tmp.name)

    return {
        "title": distilled["title"],
        "summary": distilled["summary"],
        "key_points": distilled["key_concepts"],
        "infographic_url": infographic_url,
    }
