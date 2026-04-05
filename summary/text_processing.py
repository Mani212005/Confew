"""Text normalization and cleaning utilities."""

from __future__ import annotations

import re

from summary.utils.validators import ensure_non_empty_text

_URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
_PROMO_PATTERN = re.compile(r"\b(subscribe|like|share|follow)\b", re.IGNORECASE)
_SPACE_PATTERN = re.compile(r"[ \t]+")


def _normalize_line(line: str) -> str:
    line = _URL_PATTERN.sub(" ", line)
    line = _PROMO_PATTERN.sub(" ", line)
    line = _SPACE_PATTERN.sub(" ", line)
    return line.strip()


def clean_text(raw: str) -> str:
    """Remove obvious noise while preserving headings and bullet structure."""
    content = ensure_non_empty_text(raw, "raw")
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    output_lines: list[str] = []
    blank_count = 0

    for original_line in content.split("\n"):
        normalized = _normalize_line(original_line)
        if not normalized:
            blank_count += 1
            if blank_count <= 1:
                output_lines.append("")
            continue

        blank_count = 0
        output_lines.append(normalized)

    cleaned = "\n".join(output_lines).strip()
    return ensure_non_empty_text(cleaned, "cleaned_text")
