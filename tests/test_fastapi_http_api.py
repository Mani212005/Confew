from __future__ import annotations

from fastapi.testclient import TestClient

from summary import http_api


client = TestClient(http_api.app)


def test_frontend_index_is_served():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Cofue Distillation MVP" in response.text


def test_frontend_static_js_is_served():
    response = client.get("/app/app.js")

    assert response.status_code == 200
    assert "javascript" in response.headers.get("content-type", "")
    assert "fetch(\"/process/youtube\"" in response.text


def test_post_process_youtube_returns_200_and_expected_shape(monkeypatch):
    def _ok(_payload: dict) -> dict:
        return {
            "title": "Demo",
            "summary": "Demo summary",
            "key_points": ["a", "b"],
            "infographic_url": "/tmp/demo.png",
        }

    monkeypatch.setattr(http_api, "process_youtube", _ok)

    response = client.post("/process/youtube", json={"url": "https://youtube.com/watch?v=abc123xyz00"})

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Demo"
    assert "summary" in body
    assert "key_points" in body
    assert "infographic_url" in body


def test_post_process_youtube_returns_400_when_url_missing(monkeypatch):
    from summary.exceptions import ValidationError

    def _bad(_payload: dict) -> dict:
        raise ValidationError("Missing required field: url")

    monkeypatch.setattr(http_api, "process_youtube", _bad)

    response = client.post("/process/youtube", json={})

    assert response.status_code == 400
    assert "detail" in response.json()


def test_post_process_youtube_returns_500_on_internal_error(monkeypatch):
    def _boom(_payload: dict) -> dict:
        raise RuntimeError("internal failure")

    monkeypatch.setattr(http_api, "process_youtube", _boom)

    response = client.post("/process/youtube", json={"url": "https://youtube.com/watch?v=abc123xyz00"})

    assert response.status_code == 500
    assert "detail" in response.json()
