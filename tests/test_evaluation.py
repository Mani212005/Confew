from __future__ import annotations

import pytest


@pytest.mark.evaluation
def test_summary_quality_covers_expected_key_points(import_optional):
    llm = import_optional("summary.llm_processing")

    if not hasattr(llm, "distill_content"):
        pytest.skip("distill_content is not implemented yet")

    expected_points = {"input", "processing", "output"}
    result = llm.distill_content("Input is transformed through processing into output.")

    summary_blob = " ".join(
        [
            result.get("summary", ""),
            " ".join(result.get("key_concepts", []) or result.get("key_points", [])),
        ]
    ).lower()

    hits = {p for p in expected_points if p in summary_blob}
    assert len(hits) >= 2


@pytest.mark.evaluation
def test_readability_field_exists(sample_structured_output):
    # Minimal proxy check for readability assurance pipeline.
    assert isinstance(sample_structured_output["summary"], str)
    assert len(sample_structured_output["summary"].split()) >= 4
