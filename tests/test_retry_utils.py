from __future__ import annotations

import pytest

from summary.utils.retry import call_with_retry


def test_call_with_retry_eventually_succeeds():
    state = {"count": 0}

    def _operation() -> str:
        state["count"] += 1
        if state["count"] < 3:
            raise RuntimeError("transient")
        return "ok"

    result = call_with_retry(
        _operation,
        max_retries=3,
        initial_delay_seconds=0,
        backoff_multiplier=2,
        max_delay_seconds=0,
    )

    assert result == "ok"
    assert state["count"] == 3


def test_call_with_retry_raises_after_exhausting_retries():
    def _operation() -> str:
        raise RuntimeError("always failing")

    with pytest.raises(RuntimeError):
        call_with_retry(
            _operation,
            max_retries=1,
            initial_delay_seconds=0,
            backoff_multiplier=2,
            max_delay_seconds=0,
        )
