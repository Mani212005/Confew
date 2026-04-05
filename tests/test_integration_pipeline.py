from __future__ import annotations

import pytest


@pytest.mark.integration
def test_youtube_to_summary_pipeline(import_optional):
    pipeline = import_optional("summary.pipeline")

    if not hasattr(pipeline, "process_youtube_url"):
        pytest.skip("process_youtube_url is not implemented yet")

    result = pipeline.process_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    assert isinstance(result, dict)
    assert "summary" in result
    assert "key_concepts" in result or "key_points" in result


@pytest.mark.integration
def test_pdf_to_structured_notes_pipeline(import_optional, tmp_path):
    pipeline = import_optional("summary.pipeline")

    if not hasattr(pipeline, "process_pdf"):
        pytest.skip("process_pdf is not implemented yet")

    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%mock\n")

    result = pipeline.process_pdf(str(pdf_path))

    assert isinstance(result, dict)
    assert "title" in result
    assert "summary" in result
