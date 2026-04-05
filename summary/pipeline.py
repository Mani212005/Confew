"""High-level orchestration for distillation workflows."""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

from summary.llm_processing import distill_content
from summary.text_processing import clean_text
from summary.utils.validators import ensure_non_empty_text, validate_youtube_url
from summary.visualization import generate_infographic
from summary.youtube_processing import extract_transcript


def process_text(text: str) -> dict:
    cleaned = clean_text(text)
    return distill_content(cleaned)


def process_youtube_url(url: str) -> dict:
    valid_url = validate_youtube_url(url)
    transcript = extract_transcript(valid_url)
    result = process_text(transcript)

    with NamedTemporaryFile(suffix=".png", prefix="summary_infographic_", delete=False) as tmp:
        infographic_path = generate_infographic(result, tmp.name)

    result["infographic_path"] = infographic_path
    return result


def process_pdf(pdf_path: str) -> dict:
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    raw_text = ""

    try:
        import pdfplumber  # type: ignore

        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        raw_text = "\n".join(pages)
    except Exception:
        # Accept minimal mocked PDFs in early MVP and tests.
        raw_text = path.read_bytes().decode("latin-1", errors="ignore")

    normalized = ensure_non_empty_text(raw_text, "pdf_text")
    return process_text(normalized)
