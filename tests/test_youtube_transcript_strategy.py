from __future__ import annotations

from summary.youtube_processing import _select_and_fetch_transcript


class FakeTranscript:
    def __init__(self, chunks, language_code="en", translation_languages=None):
        self._chunks = chunks
        self.language_code = language_code
        self.translation_languages = translation_languages or []

    def fetch(self):
        return self._chunks

    def translate(self, target_lang):
        return FakeTranscript(self._chunks, language_code=target_lang)


class FakeTranscriptList:
    def __init__(self, *, manual=None, generated=None, any_transcript=None, all_items=None):
        self._manual = manual
        self._generated = generated
        self._any = any_transcript
        self._all = all_items or []

    def find_manually_created_transcript(self, _langs):
        if self._manual is None:
            raise RuntimeError("no manual")
        return self._manual

    def find_generated_transcript(self, _langs):
        if self._generated is None:
            raise RuntimeError("no generated")
        return self._generated

    def find_transcript(self, _langs):
        if self._any is None:
            raise RuntimeError("no transcript")
        return self._any

    def __iter__(self):
        return iter(self._all)


def test_select_prefers_manual_transcript():
    manual = FakeTranscript([{"text": "manual"}])
    generated = FakeTranscript([{"text": "generated"}])
    listing = FakeTranscriptList(manual=manual, generated=generated)

    chunks = _select_and_fetch_transcript(
        transcript_list=listing,
        preferred_languages=["en"],
        allow_auto_translate=True,
        max_retries=0,
        initial_backoff=0,
        backoff_multiplier=2,
        max_backoff=0,
    )

    assert chunks[0]["text"] == "manual"


def test_select_falls_back_to_generated_transcript():
    generated = FakeTranscript([{"text": "generated"}])
    listing = FakeTranscriptList(manual=None, generated=generated)

    chunks = _select_and_fetch_transcript(
        transcript_list=listing,
        preferred_languages=["en"],
        allow_auto_translate=True,
        max_retries=0,
        initial_backoff=0,
        backoff_multiplier=2,
        max_backoff=0,
    )

    assert chunks[0]["text"] == "generated"


def test_select_uses_any_and_translates_when_available():
    fallback = FakeTranscript(
        [{"text": "hola"}],
        language_code="es",
        translation_languages=[{"language_code": "en"}],
    )
    listing = FakeTranscriptList(any_transcript=None, all_items=[fallback])

    chunks = _select_and_fetch_transcript(
        transcript_list=listing,
        preferred_languages=["en"],
        allow_auto_translate=True,
        max_retries=0,
        initial_backoff=0,
        backoff_multiplier=2,
        max_backoff=0,
    )

    assert chunks[0]["text"] == "hola"


def test_select_raises_when_no_transcripts_exist():
    listing = FakeTranscriptList(all_items=[])

    try:
        _select_and_fetch_transcript(
            transcript_list=listing,
            preferred_languages=["en"],
            allow_auto_translate=True,
            max_retries=0,
            initial_backoff=0,
            backoff_multiplier=2,
            max_backoff=0,
        )
        assert False, "Expected ExtractionError"
    except Exception as exc:
        assert "No transcripts available" in str(exc)
