"""FastAPI HTTP application for the distillation engine."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from summary.api import process_youtube
from summary.exceptions import ValidationError

app = FastAPI(title="AI Content Distillation Engine", version="0.1.0")
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR), name="frontend")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def frontend_index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/process/youtube")
def process_youtube_endpoint(payload: dict) -> dict:
    return process_youtube(payload)


@app.exception_handler(ValidationError)
async def validation_exception_handler(_request, exc: ValidationError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(RuntimeError)
async def runtime_exception_handler(_request, exc: RuntimeError):
    return JSONResponse(status_code=500, content={"detail": str(exc)})
