"""Configuration helpers loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    llm_provider: str
    openai_api_key: str
    openrouter_api_key: str
    openrouter_base_url: str
    openrouter_model: str
    anthropic_api_key: str
    llm_model: str
    llm_timeout_seconds: float
    transcription_provider: str
    transcription_model: str
    groq_api_key: str
    groq_base_url: str
    external_api_max_retries: int
    external_api_initial_backoff_seconds: float
    external_api_backoff_multiplier: float
    external_api_max_backoff_seconds: float
    youtube_transcript_languages: list[str]
    youtube_allow_auto_translate: bool
    youtube_enable_whisper_fallback: bool


def get_settings() -> Settings:
    provider = os.getenv("LLM_PROVIDER", "openrouter").strip().lower() or "openrouter"
    openrouter_key = (
        os.getenv("OPENROUTER_API_KEY", "").strip() or os.getenv("API_KEY", "").strip()
    )

    return Settings(
        llm_provider=provider,
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openrouter_api_key=openrouter_key,
        openrouter_base_url=(
            os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip()
            or "https://openrouter.ai/api/v1"
        ),
        # Keep this on a free-tier model by default; easy to switch later.
        openrouter_model=(
            os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-8b-instruct:free").strip()
            or "meta-llama/llama-3.3-8b-instruct:free"
        ),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", "").strip(),
        llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini",
        llm_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
        transcription_provider=(
            os.getenv("TRANSCRIPTION_PROVIDER", "openrouter").strip().lower() or "openrouter"
        ),
        transcription_model=(
            os.getenv("TRANSCRIPTION_MODEL", "openai/whisper-1").strip()
            or "openai/whisper-1"
        ),
        groq_api_key=os.getenv("GROQ_API_KEY", "").strip(),
        groq_base_url=(
            os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").strip()
            or "https://api.groq.com/openai/v1"
        ),
        external_api_max_retries=int(os.getenv("EXTERNAL_API_MAX_RETRIES", "2")),
        external_api_initial_backoff_seconds=float(
            os.getenv("EXTERNAL_API_INITIAL_BACKOFF_SECONDS", "0.5")
        ),
        external_api_backoff_multiplier=float(
            os.getenv("EXTERNAL_API_BACKOFF_MULTIPLIER", "2.0")
        ),
        external_api_max_backoff_seconds=float(
            os.getenv("EXTERNAL_API_MAX_BACKOFF_SECONDS", "5")
        ),
        youtube_transcript_languages=_parse_csv_list(
            os.getenv("YOUTUBE_TRANSCRIPT_LANGUAGES", "en,en-US")
        ),
        youtube_allow_auto_translate=_parse_bool(
            os.getenv("YOUTUBE_ALLOW_AUTO_TRANSLATE", "true")
        ),
        youtube_enable_whisper_fallback=_parse_bool(
            os.getenv("YOUTUBE_ENABLE_WHISPER_FALLBACK", "true")
        ),
    )


def _parse_csv_list(value: str) -> list[str]:
    items = [part.strip() for part in value.split(",") if part.strip()]
    return items or ["en", "en-US"]


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}
