from __future__ import annotations

import importlib
from typing import Any

import pytest


@pytest.fixture
def import_optional():
    """Import module if available, otherwise skip the calling test.

    This keeps the suite usable in early MVP phases where only part of the
    system is implemented.
    """

    def _import(module_name: str) -> Any:
        try:
            return importlib.import_module(module_name)
        except ModuleNotFoundError:
            pytest.skip(f"Module '{module_name}' is not implemented yet")

    return _import


@pytest.fixture
def sample_structured_output() -> dict[str, Any]:
    """A canonical output shape defined in tests/tests.md."""
    return {
        "title": "Neural Networks 101",
        "key_concepts": ["perceptron", "activation function", "backpropagation"],
        "summary": "A concise summary of core concepts.",
        "detailed_explanation": "Expanded explanation with context and sequence.",
        "examples": ["Binary classifier for spam filtering"],
        "visual_representation_description": "A layered network with arrows.",
        "diagram_structure": "graph TD\nA[Input] --> B[Processing]\nB --> C[Output]",
    }
