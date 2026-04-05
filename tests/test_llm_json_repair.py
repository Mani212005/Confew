from __future__ import annotations

from summary import llm_processing


def test_json_repair_handles_code_fence_and_trailing_comma():
    raw = """```json
    {
      \"title\": \"T\",
      \"key_concepts\": [\"a\", \"b\"],
      \"summary\": \"S\",
      \"detailed_explanation\": \"D\",
      \"examples\": [\"E\"],
      \"visual_representation_description\": \"V\",
      \"diagram_structure\": \"graph TD\\nA-->B\",
    }
    ```"""

    repaired = llm_processing._parse_llm_json_with_repair(raw, "source text input processing output")

    assert repaired is not None
    assert repaired["title"] == "T"
    assert repaired["key_concepts"] == ["a", "b"]


def test_json_repair_maps_key_points_and_fills_missing_fields():
    raw = "{'title': 'Title', 'key_points': ['input', 'output'], 'summary': 'Short summary'}"

    repaired = llm_processing._parse_llm_json_with_repair(raw, "Input processing output overview")

    assert repaired is not None
    assert repaired["key_concepts"] == ["input", "output"]
    assert repaired["detailed_explanation"]
    assert repaired["examples"]
    assert repaired["diagram_structure"]


def test_json_repair_returns_none_for_non_json_payload():
    raw = "This is not JSON at all"

    repaired = llm_processing._parse_llm_json_with_repair(raw, "source")

    assert repaired is None
