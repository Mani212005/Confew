from __future__ import annotations

import json
import logging

from summary.utils.telemetry import get_logger, log_event


def test_log_event_emits_structured_json():
    logger = get_logger("test")
    captured_messages: list[str] = []

    class _CaptureHandler(logging.Handler):
        def emit(self, record):
            captured_messages.append(record.getMessage())

    capture_handler = _CaptureHandler(level=logging.INFO)
    logger.logger.addHandler(capture_handler)

    try:
        log_event(logger, "sample_event", foo="bar", status=200)
    finally:
        logger.logger.removeHandler(capture_handler)

    assert captured_messages
    payload = json.loads(captured_messages[-1])
    assert payload["event"] == "sample_event"
    assert payload["component"] == "test"
    assert payload["foo"] == "bar"
    assert payload["status"] == 200
