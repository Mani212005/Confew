## Cofue MVP

Backend and frontend MVP are served by FastAPI.

### Run

```bash
"/Users/manijoshi/Summary /.venv/bin/python" -m uvicorn summary.http_api:app --reload
```

### Endpoints

- `GET /health`
- `POST /process/youtube`
- `GET /` (frontend app)

### Frontend Flow

1. Open `http://127.0.0.1:8000/`.
2. Paste a YouTube URL.
3. Click `Generate` to call `POST /process/youtube`.
4. View summary, key points, and infographic path.
