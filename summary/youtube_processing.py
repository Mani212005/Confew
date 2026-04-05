"""YouTube transcript extraction with fallback behavior."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from summary.config import get_settings
from summary.exceptions import ExtractionError, ValidationError
from summary.utils.retry import call_with_retry
from summary.utils.telemetry import exception_to_fields, get_logger, log_event, new_operation_id
from summary.utils.validators import extract_video_id, validate_youtube_url

logger = get_logger("extraction")


def fetch_youtube_transcript(url: str) -> str:
    """Fetch transcript using youtube-transcript-api when available."""
    valid_url = validate_youtube_url(url)
    video_id = extract_video_id(valid_url)
    operation_id = new_operation_id()
    log_event(
        logger,
        "youtube_transcript_fetch_started",
        operation_id=operation_id,
        video_id=video_id,
    )

    settings = get_settings()

    try:
        from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore

        transcript_list = call_with_retry(
            lambda: YouTubeTranscriptApi.list_transcripts(video_id),
            max_retries=settings.external_api_max_retries,
            initial_delay_seconds=settings.external_api_initial_backoff_seconds,
            backoff_multiplier=settings.external_api_backoff_multiplier,
            max_delay_seconds=settings.external_api_max_backoff_seconds,
        )

        chunks = _select_and_fetch_transcript(
            transcript_list=transcript_list,
            preferred_languages=settings.youtube_transcript_languages,
            allow_auto_translate=settings.youtube_allow_auto_translate,
            max_retries=settings.external_api_max_retries,
            initial_backoff=settings.external_api_initial_backoff_seconds,
            backoff_multiplier=settings.external_api_backoff_multiplier,
            max_backoff=settings.external_api_max_backoff_seconds,
        )
        transcript = " ".join(chunk.get("text", "") for chunk in chunks).strip()
        if transcript:
            log_event(
                logger,
                "youtube_transcript_fetch_succeeded",
                operation_id=operation_id,
                video_id=video_id,
            )
            return transcript
        raise ExtractionError("Transcript returned empty content")
    except ImportError as exc:
        raise ExtractionError(
            "youtube-transcript-api is not installed. Install dependency and retry."
        ) from exc
    except ValidationError:
        raise
    except Exception as exc:  # noqa: BLE001
        log_event(
            logger,
            "youtube_transcript_fetch_failed",
            level=40,
            operation_id=operation_id,
            video_id=video_id,
            **exception_to_fields(exc),
        )
        raise ExtractionError(f"Unable to fetch YouTube transcript: {exc}") from exc


def whisper_transcribe(url: str) -> str:
    """Fallback transcript path when direct transcript fetching fails."""
    valid_url = validate_youtube_url(url)
    operation_id = new_operation_id()
    log_event(logger, "whisper_fallback_started", operation_id=operation_id)

    with TemporaryDirectory(prefix="cofue_whisper_") as tmp_dir:
        audio_path = _download_audio_from_youtube(valid_url, Path(tmp_dir))
        transcript = _transcribe_audio_file(audio_path)

    if not transcript.strip():
        raise ExtractionError("Whisper transcription returned empty content")

    log_event(logger, "whisper_fallback_succeeded", operation_id=operation_id)

    return transcript


def _download_audio_from_youtube(url: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    settings = get_settings()

    try:
        import yt_dlp  # type: ignore
    except ImportError as exc:
        raise ExtractionError("yt-dlp is required for Whisper fallback") from exc

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / "%(id)s.%(ext)s"),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            def _request() -> dict:
                return ydl.extract_info(url, download=True)

            info = call_with_retry(
                _request,
                max_retries=settings.external_api_max_retries,
                initial_delay_seconds=settings.external_api_initial_backoff_seconds,
                backoff_multiplier=settings.external_api_backoff_multiplier,
                max_delay_seconds=settings.external_api_max_backoff_seconds,
            )
            downloads = info.get("requested_downloads") or []
            if downloads and downloads[0].get("filepath"):
                candidate = Path(downloads[0]["filepath"])
                if candidate.exists():
                    return candidate

            guessed = Path(ydl.prepare_filename(info))
            if guessed.exists():
                return guessed

            video_id = info.get("id", "")
            if video_id:
                matches = list(output_dir.glob(f"{video_id}.*"))
                if matches:
                    return matches[0]
    except Exception as exc:  # noqa: BLE001
        raise ExtractionError(f"Unable to download YouTube audio for Whisper fallback: {exc}") from exc

    raise ExtractionError("Downloaded audio file not found")


def _transcribe_audio_file(audio_path: Path) -> str:
    settings = get_settings()

    provider = settings.transcription_provider
    model = settings.transcription_model

    try:
        from openai import OpenAI  # type: ignore
    except ImportError as exc:
        raise ExtractionError("openai package is required for audio transcription") from exc

    client = None
    extra_headers = None

    if provider == "openai":
        if not settings.openai_api_key:
            raise ExtractionError("OPENAI_API_KEY is required for transcription provider 'openai'")
        client = OpenAI(api_key=settings.openai_api_key, timeout=settings.llm_timeout_seconds)
    elif provider == "groq":
        if not settings.groq_api_key:
            raise ExtractionError("GROQ_API_KEY is required for transcription provider 'groq'")
        client = OpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
            timeout=settings.llm_timeout_seconds,
        )
    elif provider == "openrouter":
        if not settings.openrouter_api_key:
            raise ExtractionError(
                "OPENROUTER_API_KEY (or API_KEY) is required for transcription provider 'openrouter'"
            )
        client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            timeout=settings.llm_timeout_seconds,
        )
        extra_headers = {
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Cofue Distillation Engine",
        }
    else:
        raise ExtractionError(
            f"Unsupported transcription provider '{provider}'. Use one of: openrouter, openai, groq"
        )

    try:
        with audio_path.open("rb") as audio_file:
            kwargs = {"model": model, "file": audio_file}
            if extra_headers is not None:
                kwargs["extra_headers"] = extra_headers

            def _request() -> object:
                return client.audio.transcriptions.create(**kwargs)

            response = call_with_retry(
                _request,
                max_retries=settings.external_api_max_retries,
                initial_delay_seconds=settings.external_api_initial_backoff_seconds,
                backoff_multiplier=settings.external_api_backoff_multiplier,
                max_delay_seconds=settings.external_api_max_backoff_seconds,
            )
            transcript = getattr(response, "text", "")
            return str(transcript).strip()
    except Exception as exc:  # noqa: BLE001
        raise ExtractionError(f"Whisper transcription failed: {exc}") from exc


def extract_transcript(url: str) -> str:
    """Extract transcript, using Whisper fallback when transcript is missing."""
    valid_url = validate_youtube_url(url)
    operation_id = new_operation_id()

    try:
        transcript = fetch_youtube_transcript(valid_url)
        if transcript.strip():
            return transcript
        raise ExtractionError("Transcript is empty")
    except ValidationError:
        raise
    except Exception as exc:
        log_event(
            logger,
            "youtube_transcript_primary_failed_using_fallback",
            level=30,
            operation_id=operation_id,
            **exception_to_fields(exc),
        )
        fallback = whisper_transcribe(valid_url)
        if not fallback.strip():
            raise ExtractionError("Both transcript extraction and fallback failed")
        return fallback


def _select_and_fetch_transcript(
    *,
    transcript_list: Any,
    preferred_languages: list[str],
    allow_auto_translate: bool,
    max_retries: int,
    initial_backoff: float,
    backoff_multiplier: float,
    max_backoff: float,
) -> list[dict]:
    """Pick the best transcript strategy and fetch transcript chunks."""

    candidate = None

    # Prefer manual transcripts in requested languages.
    try:
        candidate = transcript_list.find_manually_created_transcript(preferred_languages)
    except Exception:
        candidate = None

    # Fall back to generated transcripts if needed.
    if candidate is None:
        try:
            candidate = transcript_list.find_generated_transcript(preferred_languages)
        except Exception:
            candidate = None

    # Fall back to any transcript in requested languages.
    if candidate is None:
        try:
            candidate = transcript_list.find_transcript(preferred_languages)
        except Exception:
            candidate = None

    # Last resort: use first available transcript and auto-translate if requested.
    if candidate is None:
        available = list(transcript_list)
        if not available:
            raise ExtractionError("No transcripts available for this video")

        candidate = available[0]
        if allow_auto_translate and preferred_languages:
            target_lang = preferred_languages[0]
            if getattr(candidate, "language_code", "") != target_lang:
                try:
                    translatable = set(getattr(candidate, "translation_languages", []) or [])
                    normalized = set()
                    for item in translatable:
                        if isinstance(item, dict):
                            code = item.get("language_code")
                            if code:
                                normalized.add(code)
                        elif isinstance(item, str):
                            normalized.add(item)

                    if target_lang in normalized:
                        candidate = candidate.translate(target_lang)
                except Exception:
                    pass

    return call_with_retry(
        lambda: candidate.fetch(),
        max_retries=max_retries,
        initial_delay_seconds=initial_backoff,
        backoff_multiplier=backoff_multiplier,
        max_delay_seconds=max_backoff,
    )
