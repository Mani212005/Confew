from __future__ import annotations

import pytest


def test_post_process_youtube_valid_request(import_optional):
    api = import_optional("summary.api")

    if not hasattr(api, "process_youtube"):
        pytest.skip("process_youtube is not implemented yet")

    original_extract = api.extract_transcript
    api.extract_transcript = lambda _url: "Input processing output educational transcript"

    try:
        response = api.process_youtube({"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    finally:
        api.extract_transcript = original_extract

    assert isinstance(response, dict)
    assert "title" in response
    assert "summary" in response
    assert "key_points" in response


def test_post_process_youtube_missing_url_returns_400_shape(import_optional):
    api = import_optional("summary.api")

    if not hasattr(api, "process_youtube"):
        pytest.skip("process_youtube is not implemented yet")

    with pytest.raises((ValueError, KeyError)):
        api.process_youtube({})


def test_post_process_youtube_server_failure_returns_error(import_optional, monkeypatch):
    api = import_optional("summary.api")

    if not hasattr(api, "process_youtube"):
        pytest.skip("process_youtube is not implemented yet")

    if not hasattr(api, "extract_transcript"):
        pytest.skip("extract_transcript hook not available for failure simulation")

    def _boom(_url: str):
        raise RuntimeError("internal failure")

    monkeypatch.setattr(api, "extract_transcript", _boom)

    with pytest.raises(RuntimeError):
        api.process_youtube({"url": "https://www.youtube.com/watch?v=test"})
