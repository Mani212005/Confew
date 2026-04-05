from __future__ import annotations

import time

import pytest


@pytest.mark.performance
def test_short_content_processing_under_30_seconds(import_optional):
    pipeline = import_optional("summary.pipeline")

    if not hasattr(pipeline, "process_text"):
        pytest.skip("process_text is not implemented yet")

    start = time.perf_counter()
    _ = pipeline.process_text("Short educational snippet about recursion.")
    elapsed = time.perf_counter() - start

    assert elapsed < 30


@pytest.mark.performance
def test_concurrent_processing_placeholder():
    # Placeholder until a load test harness (Locust/k6) is integrated.
    # This test ensures the performance marker is wired in CI.
    assert True
