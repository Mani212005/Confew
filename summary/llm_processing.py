"""LLM-backed content distillation with deterministic fallback."""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any

from summary.config import get_settings
from summary.exceptions import DistillationError
from summary.utils.retry import call_with_retry
from summary.utils.validators import ensure_non_empty_text

_REQUIRED_FIELDS = {
    "title",
    "key_concepts",
    "summary",
    "detailed_explanation",
    "examples",
    "visual_representation_description",
    "diagram_structure",
}


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())


def _heuristic_distill(text: str) -> dict[str, Any]:
    words = _tokenize(text)
    common = [w for w, _ in Counter(words).most_common(8)]

    key_concepts = []
    for keyword in ["input", "processing", "output"]:
        if keyword in words:
            key_concepts.append(keyword)
    for word in common:
        if word not in key_concepts:
            key_concepts.append(word)
        if len(key_concepts) >= 5:
            break

    if not key_concepts:
        key_concepts = ["learning", "summary", "concepts"]

    summary = (
        "This content explains how input is transformed through processing "
        "to produce clear output and practical understanding."
    )

    return {
        "title": "Distilled Learning Summary",
        "key_concepts": key_concepts,
        "summary": summary,
        "detailed_explanation": (
            "The material is normalized into a structured flow: capture the source input, "
            "process it into concise insights, and deliver output that is easier to revise."
        ),
        "examples": ["Transform a long tutorial into concise revision notes."],
        "visual_representation_description": (
            "A left-to-right flow showing input, processing stages, and final output artifacts."
        ),
        "diagram_structure": "graph TD\nA[Input] --> B[Processing]\nB --> C[Output]",
    }


def _validate_output(payload: dict[str, Any]) -> dict[str, Any]:
    missing = _REQUIRED_FIELDS.difference(payload.keys())
    if missing:
        raise DistillationError(f"Missing output fields: {sorted(missing)}")

    for key in _REQUIRED_FIELDS:
        value = payload.get(key)
        if isinstance(value, str) and not value.strip():
            raise DistillationError(f"Output field '{key}' is empty")
        if isinstance(value, list) and not value:
            raise DistillationError(f"Output field '{key}' is empty")
        if value is None:
            raise DistillationError(f"Output field '{key}' is None")

    return payload


def _openai_distill(text: str) -> dict[str, Any] | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None

    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=settings.openai_api_key, timeout=settings.llm_timeout_seconds)
        prompt = (
            "Return JSON with keys: title, key_concepts, summary, detailed_explanation, "
            "examples, visual_representation_description, diagram_structure."
        )

        def _request() -> Any:
            return client.chat.completions.create(
                model=settings.llm_model,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
            )

        response = call_with_retry(
            _request,
            max_retries=settings.external_api_max_retries,
            initial_delay_seconds=settings.external_api_initial_backoff_seconds,
            backoff_multiplier=settings.external_api_backoff_multiplier,
            max_delay_seconds=settings.external_api_max_backoff_seconds,
        )

        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        return None

    return None


def _openrouter_distill(text: str) -> dict[str, Any] | None:
    settings = get_settings()
    if not settings.openrouter_api_key:
        return None

    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            timeout=settings.llm_timeout_seconds,
        )

        prompt = (
            "Return JSON with keys: title, key_concepts, summary, detailed_explanation, "
            "examples, visual_representation_description, diagram_structure."
        )

        def _request() -> Any:
            return client.chat.completions.create(
                model=settings.openrouter_model,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "Cofue Distillation Engine",
                },
            )

        response = call_with_retry(
            _request,
            max_retries=settings.external_api_max_retries,
            initial_delay_seconds=settings.external_api_initial_backoff_seconds,
            backoff_multiplier=settings.external_api_backoff_multiplier,
            max_delay_seconds=settings.external_api_max_backoff_seconds,
        )

        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        return None

    return None


def distill_content(raw_text: str) -> dict[str, Any]:
    """Distill cleaned text into the required structured output format."""
    text = ensure_non_empty_text(raw_text, "raw_text")
    settings = get_settings()

    llm_output: dict[str, Any] | None = None
    if settings.llm_provider == "openrouter":
        llm_output = _openrouter_distill(text)
    elif settings.llm_provider == "openai":
        llm_output = _openai_distill(text)

    if llm_output is None:
        llm_output = _heuristic_distill(text)

    return _validate_output(llm_output)
