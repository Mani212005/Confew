"""LLM-backed content distillation with deterministic fallback."""

from __future__ import annotations

import ast
import json
import re
from collections import Counter
from typing import Any

from summary.config import get_settings
from summary.exceptions import DistillationError
from summary.utils.retry import call_with_retry
from summary.utils.telemetry import exception_to_fields, get_logger, log_event, new_operation_id
from summary.utils.validators import ensure_non_empty_text

logger = get_logger("llm")

_REQUIRED_FIELDS = {
    "title",
    "key_concepts",
    "summary",
    "detailed_explanation",
    "examples",
    "visual_representation_description",
    "diagram_structure",
}

_TEXT_FIELDS = {
    "title",
    "summary",
    "detailed_explanation",
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


def _extract_json_object_block(raw: str) -> str | None:
    start = raw.find("{")
    if start == -1:
        return None

    depth = 0
    for idx in range(start, len(raw)):
        char = raw[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return raw[start : idx + 1]
    return None


def _coerce_payload_dict(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def _normalize_llm_payload(payload: dict[str, Any], source_text: str) -> dict[str, Any]:
    normalized = dict(payload)

    if "key_concepts" not in normalized and "key_points" in normalized:
        normalized["key_concepts"] = normalized.get("key_points")

    if isinstance(normalized.get("key_concepts"), str):
        normalized["key_concepts"] = [
            part.strip() for part in normalized["key_concepts"].split(",") if part.strip()
        ]

    if not isinstance(normalized.get("examples"), list):
        examples_value = normalized.get("examples")
        if isinstance(examples_value, str) and examples_value.strip():
            normalized["examples"] = [examples_value.strip()]

    for key in _TEXT_FIELDS:
        value = normalized.get(key)
        if value is not None and not isinstance(value, str):
            normalized[key] = str(value)

    fallback = _heuristic_distill(source_text)
    for key, fallback_value in fallback.items():
        value = normalized.get(key)
        if value is None:
            normalized[key] = fallback_value
            continue

        if isinstance(value, str) and not value.strip():
            normalized[key] = fallback_value
            continue

        if isinstance(value, list) and not value:
            normalized[key] = fallback_value

    return normalized


def _parse_llm_json_with_repair(raw: str, source_text: str) -> dict[str, Any] | None:
    candidates: list[str] = []

    stripped = raw.strip()
    if stripped:
        candidates.append(stripped)

    # Remove markdown fences such as ```json ... ```.
    without_fence = re.sub(r"^```(?:json)?\s*|\s*```$", "", stripped, flags=re.IGNORECASE)
    if without_fence and without_fence not in candidates:
        candidates.append(without_fence.strip())

    extracted = _extract_json_object_block(without_fence or stripped)
    if extracted and extracted not in candidates:
        candidates.append(extracted.strip())

    parsed_payload: dict[str, Any] | None = None

    for candidate in candidates:
        try:
            parsed_payload = _coerce_payload_dict(json.loads(candidate))
            if parsed_payload is not None:
                break
        except Exception:
            pass

        try:
            repaired = re.sub(r",\s*([}\]])", r"\1", candidate)
            parsed_payload = _coerce_payload_dict(json.loads(repaired))
            if parsed_payload is not None:
                break
        except Exception:
            pass

        try:
            parsed_payload = _coerce_payload_dict(ast.literal_eval(candidate))
            if parsed_payload is not None:
                break
        except Exception:
            pass

    if parsed_payload is None:
        log_event(logger, "llm_json_repair_failed", level=30)
        return None

    normalized = _normalize_llm_payload(parsed_payload, source_text)
    try:
        log_event(logger, "llm_json_repair_succeeded")
        return _validate_output(normalized)
    except DistillationError:
        log_event(logger, "llm_json_repair_validation_failed", level=30)
        return None


def _openai_distill(text: str) -> dict[str, Any] | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None

    operation_id = new_operation_id()

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
        return _parse_llm_json_with_repair(content, text)
    except Exception as exc:
        log_event(
            logger,
            "llm_provider_call_failed",
            level=40,
            operation_id=operation_id,
            provider="openai",
            **exception_to_fields(exc),
        )
        return None

    return None


def _openrouter_distill(text: str) -> dict[str, Any] | None:
    settings = get_settings()
    if not settings.openrouter_api_key:
        return None

    operation_id = new_operation_id()

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
        return _parse_llm_json_with_repair(content, text)
    except Exception as exc:
        log_event(
            logger,
            "llm_provider_call_failed",
            level=40,
            operation_id=operation_id,
            provider="openrouter",
            **exception_to_fields(exc),
        )
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
        log_event(logger, "llm_fallback_to_heuristic", level=30, provider=settings.llm_provider)
        llm_output = _heuristic_distill(text)

    return _validate_output(llm_output)
