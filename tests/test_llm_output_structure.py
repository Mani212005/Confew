from __future__ import annotations

import pytest

REQUIRED_FIELDS = {
    "title",
    "key_concepts",
    "summary",
    "detailed_explanation",
    "examples",
    "visual_representation_description",
    "diagram_structure",
}


def test_structured_output_contains_required_sections(import_optional):
    llm = import_optional("summary.llm_processing")

    if not hasattr(llm, "distill_content"):
        pytest.skip("distill_content is not implemented yet")

    output = llm.distill_content("Sample educational transcript")

    assert isinstance(output, dict)
    assert REQUIRED_FIELDS.issubset(output.keys())


def test_structured_output_has_no_empty_fields(sample_structured_output):
    for key, value in sample_structured_output.items():
        if isinstance(value, str):
            assert value.strip() != "", f"Field '{key}' should not be empty"
        elif isinstance(value, list):
            assert len(value) > 0, f"Field '{key}' should not be empty"
        else:
            assert value is not None, f"Field '{key}' should not be None"
