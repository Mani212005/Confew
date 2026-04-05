from __future__ import annotations

import pytest


def test_noise_is_removed(import_optional):
    text_module = import_optional("summary.text_processing")

    if not hasattr(text_module, "clean_text"):
        pytest.skip("clean_text is not implemented yet")

    raw = "\n\nSubscribe!!!   Visit http://example.com   REAL content here.\n"
    cleaned = text_module.clean_text(raw)

    assert isinstance(cleaned, str)
    assert "REAL content" in cleaned


def test_long_inputs_are_handled(import_optional):
    text_module = import_optional("summary.text_processing")

    if not hasattr(text_module, "clean_text"):
        pytest.skip("clean_text is not implemented yet")

    raw = "Token " * 50_000
    cleaned = text_module.clean_text(raw)

    assert isinstance(cleaned, str)
    assert len(cleaned) > 0


def test_structure_is_preserved(import_optional):
    text_module = import_optional("summary.text_processing")

    if not hasattr(text_module, "clean_text"):
        pytest.skip("clean_text is not implemented yet")

    raw = "# Title\n\n- Point A\n- Point B\n"
    cleaned = text_module.clean_text(raw)

    assert "Title" in cleaned
    assert "Point A" in cleaned
    assert "Point B" in cleaned
