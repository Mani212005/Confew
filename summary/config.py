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
    )
