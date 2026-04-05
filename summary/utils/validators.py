"""Input validation helpers used by API and pipeline layers."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from summary.exceptions import ValidationError


def validate_process_payload(payload: dict) -> str:
    if not isinstance(payload, dict):
        raise ValidationError("Payload must be a dictionary")

    if "url" not in payload:
        raise ValidationError("Missing required field: url")

    url = payload.get("url")
    if not isinstance(url, str) or not url.strip():
        raise ValidationError("Field 'url' must be a non-empty string")

    return url.strip()


def extract_video_id(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()

    if "youtube.com" in host:
        query = parse_qs(parsed.query)
        video_id = query.get("v", [""])[0].strip()
        if video_id:
            return video_id

    if "youtu.be" in host:
        video_id = parsed.path.strip("/")
        if video_id:
            return video_id

    raise ValidationError("Invalid YouTube URL")


def validate_youtube_url(url: str) -> str:
    if not isinstance(url, str) or not url.strip():
        raise ValidationError("YouTube URL must be a non-empty string")

    cleaned = url.strip()
    _ = extract_video_id(cleaned)
    return cleaned


def ensure_non_empty_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} must be a non-empty string")
    return value.strip()
