"""FastAPI HTTP application for the distillation engine."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from summary.api import process_youtube
from summary.exceptions import ValidationError
from summary.utils.telemetry import exception_to_fields, get_logger, log_event, new_operation_id

app = FastAPI(title="AI Content Distillation Engine", version="0.1.0")
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
logger = get_logger("http")

if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR), name="frontend")


@app.middleware("http")
async def request_telemetry_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", new_operation_id())
    request.state.request_id = request_id
    log_event(
        logger,
        "http_request_started",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    log_event(
        logger,
        "http_request_finished",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )
    return response


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
async def validation_exception_handler(request: Request, exc: ValidationError):
    request_id = getattr(request.state, "request_id", new_operation_id())
    log_event(
        logger,
        "http_validation_error",
        level=logging.WARNING,
        request_id=request_id,
        path=request.url.path,
        **exception_to_fields(exc),
    )
    response = JSONResponse(status_code=400, content={"detail": str(exc)})
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(RuntimeError)
async def runtime_exception_handler(request: Request, exc: RuntimeError):
    request_id = getattr(request.state, "request_id", new_operation_id())
    log_event(
        logger,
        "http_runtime_error",
        level=logging.ERROR,
        request_id=request_id,
        path=request.url.path,
        **exception_to_fields(exc),
    )
    response = JSONResponse(status_code=500, content={"detail": str(exc)})
    response.headers["X-Request-ID"] = request_id
    return response
