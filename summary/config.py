"""Configuration helpers loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    llm_provider: str
    openai_api_key: str
    anthropic_api_key: str
    llm_model: str
    llm_timeout_seconds: float


def get_settings() -> Settings:
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower() or "openai"
    return Settings(
        llm_provider=provider,
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", "").strip(),
        llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini",
        llm_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
    )
