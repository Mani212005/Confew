## Cofue MVP

Backend and frontend MVP are served by FastAPI.

### LLM Setup (.env)

Create a `.env` file from `.env.example` and set your provider settings.

Recommended for now (free model):

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=meta-llama/llama-3.3-8b-instruct:free
```

Switch later to paid models by updating only `OPENROUTER_MODEL`.

### Whisper Fallback Setup

The YouTube fallback transcription path is now real (audio download + transcription).

Required:

- Python deps: `yt-dlp`, `youtube-transcript-api`, `openai`
- System dependency: `ffmpeg` (recommended for broad media compatibility)

Optional provider config in `.env`:

```env
TRANSCRIPTION_PROVIDER=openrouter
TRANSCRIPTION_MODEL=openai/whisper-1
```

You can also set `TRANSCRIPTION_PROVIDER=openai` or `TRANSCRIPTION_PROVIDER=groq` and provide matching keys.

### Run

```bash
"/Users/manijoshi/Summary /.venv/bin/python" -m uvicorn summary.http_api:app --reload
```

### Telemetry

Structured JSON logs are emitted for:

- HTTP request lifecycle and failures
- API processing failures
- Transcript extraction and fallback failures
- LLM provider failures and heuristic fallback usage

Set `LOG_LEVEL` in `.env` (for example: `INFO`, `WARNING`, `ERROR`).

### Endpoints

- `GET /health`
- `POST /process/youtube`
- `GET /` (frontend app)

### Frontend Flow

1. Open `http://127.0.0.1:8000/`.
2. Paste a YouTube URL.
3. Click `Generate` to call `POST /process/youtube`.
4. View summary, key points, and infographic path.
