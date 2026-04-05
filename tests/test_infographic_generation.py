from __future__ import annotations

from pathlib import Path

import pytest


def test_infographic_generation_success(import_optional, tmp_path):
    viz = import_optional("summary.visualization")

    if not hasattr(viz, "generate_infographic"):
        pytest.skip("generate_infographic is not implemented yet")

    out_path = tmp_path / "infographic.png"
    result = viz.generate_infographic(
        data={"title": "Demo", "summary": "Demo summary"},
        output_path=out_path,
    )

    generated_path = Path(result) if result else out_path
    assert generated_path.exists()


def test_infographic_layout_is_consistent(import_optional):
    viz = import_optional("summary.visualization")

    if not hasattr(viz, "build_infographic_layout"):
        pytest.skip("build_infographic_layout is not implemented yet")

    layout = viz.build_infographic_layout(
        {
            "title": "Topic",
            "key_concepts": ["A", "B"],
            "summary": "S",
        }
    )

    assert isinstance(layout, dict)
    assert "sections" in layout
    assert len(layout["sections"]) >= 2
