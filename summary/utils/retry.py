"""Retry and exponential backoff helpers for external service calls."""

from __future__ import annotations

import time
from typing import Callable, TypeVar

T = TypeVar("T")


def call_with_retry(
    operation: Callable[[], T],
    *,
    max_retries: int,
    initial_delay_seconds: float,
    backoff_multiplier: float,
    max_delay_seconds: float,
    retry_on: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """Run an operation with exponential backoff retries.

    max_retries means additional attempts after the initial attempt.
    """
    if max_retries < 0:
        max_retries = 0

    delay = max(0.0, initial_delay_seconds)
    attempts = max_retries + 1
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except retry_on as exc:
            last_error = exc
            if attempt >= attempts:
                break

            if delay > 0:
                time.sleep(min(delay, max_delay_seconds))
            delay = min(max_delay_seconds, max(0.01, delay * max(1.0, backoff_multiplier)))

    if last_error is not None:
        raise last_error

    raise RuntimeError("Retry operation failed without a captured exception")
