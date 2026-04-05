"""Structured logging helpers for production telemetry."""

from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Any

_LOGGER_NAME = "cofue"


def _get_root_logger() -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return logger

    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, level_name, logging.INFO))
    logger.propagate = False
    return logger


def get_logger(component: str) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(_get_root_logger(), {"component": component})


def new_operation_id() -> str:
    return str(uuid.uuid4())


def log_event(
    logger: logging.LoggerAdapter,
    event: str,
    *,
    level: int = logging.INFO,
    **fields: Any,
) -> None:
    payload = {
        "event": event,
        "component": logger.extra.get("component", "unknown"),
        **fields,
    }
    logger.log(level, json.dumps(payload, default=str, ensure_ascii=True))


def exception_to_fields(exc: Exception) -> dict[str, str]:
    return {
        "error_type": exc.__class__.__name__,
        "error_message": str(exc),
    }
