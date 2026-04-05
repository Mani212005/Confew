from __future__ import annotations


def test_required_output_keys_regression_guard(sample_structured_output):
    # Regression guard for required output structure from spec.
    expected = {
        "title",
        "key_concepts",
        "summary",
        "detailed_explanation",
        "examples",
        "visual_representation_description",
        "diagram_structure",
    }
    assert set(sample_structured_output) == expected
