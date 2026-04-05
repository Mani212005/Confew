# TODO - Cofue AI Content Distillation Engine

This checklist shows both completed work and remaining scope from `SPEC.md` and current implementation.

Legend:
- `[x]` Done
- `[ ]` Pending

## High Priority

- [x] Build backend package structure (`summary/`) with modular pipeline files.
- [x] Implement YouTube URL validation and transcript extraction flow with fallback behavior.
- [x] Implement text cleaning/normalization layer.
- [x] Implement structured distillation output contract (7 required sections).
- [x] Implement basic infographic layout + generation flow.
- [x] Build orchestration pipeline (`process_text`, `process_youtube_url`, `process_pdf`).
- [x] Implement API processing boundary (`process_youtube(payload)`).
- [x] Add real FastAPI app with `POST /process/youtube` and `GET /health`.
- [x] Build frontend MVP layout and connect it to `POST /process/youtube`.
- [x] Add and pass test suite for unit/integration/API/performance/evaluation placeholders.
- [x] Add `.env` loading and OpenRouter support with free model defaults.
- [x] Add `.env` safety in `.gitignore` and provide `.env.example`.
- [ ] Implement robust YouTube extraction using `youtube-transcript-api` end-to-end in production mode.
- [x] Implement real Whisper fallback transcription pipeline (audio fetch + transcription), not placeholder-only fallback text.
- [x] Add retry/backoff and stronger error handling for external API calls (LLM + transcript services).
- [ ] Add output JSON repair/validation fallback when LLM returns malformed JSON.
- [ ] Add production logging/telemetry for extraction, LLM, and API failures.

## Have to Be done

- [ ] Implement Web Page input pipeline (URL -> extracted clean article text).
- [ ] Implement Image/Screenshot OCR pipeline (image -> extracted text).
- [ ] Improve PDF extraction quality and edge-case handling for real documents.
- [ ] Add Mermaid/Graphviz diagram generation from distilled concepts.
- [ ] Improve infographic quality (HTML/CSS render pipeline + better typography/layout consistency).
- [ ] Add Notes export (Markdown output/download).
- [ ] Add stronger API schema validation with Pydantic request/response models.
- [ ] Add API-level tests for schema, headers, and invalid content types.
- [ ] Add CI workflow (GitHub Actions) to run tests on each commit/PR.
- [ ] Add environment profiles and docs for dev/stage/prod setup.
- [ ] Add request timeout/rate limit settings at API boundary.
- [ ] Add frontend UX hardening (better loading state, retry action, polished error states).

## Optional

- [ ] Add local persistence for processed outputs (Markdown/history cache).
- [ ] Add Notion integration for knowledge-base publishing.
- [ ] Add vector DB integration (FAISS/Pinecone) for semantic search.
- [ ] Add dashboard for saved content and history browsing.
- [ ] Add search/filtering in frontend.
- [ ] Add drag-and-drop uploads for PDF/images.
- [ ] Add dark mode support.
- [ ] Add flashcard generation.
- [ ] Add quiz generation.
- [ ] Add multi-video knowledge synthesis.
- [ ] Add personalized learning paths.
- [ ] Add social media auto-posting.
- [ ] Add advanced E2E browser tests for full user journeys.

## Notes

- Current test status is green (`28 passed`) including backend + HTTP + frontend MVP route checks.
- Frontend is currently an MVP static UI served by FastAPI and can be upgraded to React/Vite later.
