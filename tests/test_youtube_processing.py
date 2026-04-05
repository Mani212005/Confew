from __future__ import annotations

import pytest


def test_valid_youtube_url_returns_transcript(import_optional):
    yt = import_optional("summary.youtube_processing")

    if not hasattr(yt, "extract_transcript"):
        pytest.skip("extract_transcript is not implemented yet")

    original_fetch = yt.fetch_youtube_transcript
    yt.fetch_youtube_transcript = lambda _url: "Transcript content from source"

    try:
        transcript = yt.extract_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert isinstance(transcript, str)
        assert transcript.strip() != ""
    finally:
        yt.fetch_youtube_transcript = original_fetch


def test_invalid_youtube_url_raises_value_error(import_optional):
    yt = import_optional("summary.youtube_processing")

    if not hasattr(yt, "extract_transcript"):
        pytest.skip("extract_transcript is not implemented yet")

    with pytest.raises((ValueError, RuntimeError)):
        yt.extract_transcript("not-a-valid-youtube-url")


def test_no_transcript_uses_whisper_fallback(import_optional, monkeypatch):
    yt = import_optional("summary.youtube_processing")

    required = ["extract_transcript", "fetch_youtube_transcript", "whisper_transcribe"]
    if not all(hasattr(yt, name) for name in required):
        pytest.skip("Fallback flow functions are not implemented yet")

    def _no_transcript(_url: str):
        raise RuntimeError("No transcript available")

    def _whisper(_url: str):
        return "Fallback transcript from Whisper"

    monkeypatch.setattr(yt, "fetch_youtube_transcript", _no_transcript)
    monkeypatch.setattr(yt, "whisper_transcribe", _whisper)

    transcript = yt.extract_transcript("https://www.youtube.com/watch?v=abc123xyz00")
    assert transcript == "Fallback transcript from Whisper"
