# Moonshot Backend

Python FastAPI backend integrating scribe2fhir (SDK) and EkaScribe (REST API).

## Setup

1. Create a virtualenv and install dependencies:

   **Windows (PowerShell):**
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

   **macOS/Linux:**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and set:

   - `EKA_API_TOKEN` (required) – Bearer token for Eka API (file-upload, init, status).
   - `EKA_CLIENT_ID`, `EKA_CLIENT_SECRET` (optional) – for future token refresh.

3. If using scribe2fhir: uncomment `scribe2fhir` in `requirements.txt`, run `pip install -r requirements.txt` again, and add any env vars its SDK needs. If the package is not on public PyPI, install from your private index.

## Run

From the `backend` directory with the venv activated:

```bash
uvicorn main:app --reload --port 8000
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## API

- **EkaScribe**: `POST /api/ekascribe/transcribe` – multipart audio file(s); returns transcription result after presigned URL → S3 upload → init → poll.
- **scribe2fhir**: `GET /api/scribe2fhir/health` – SDK availability; `POST /api/scribe2fhir/submit` – document submit (implement once SDK API is confirmed).

Next.js can call `http://localhost:8000` or use a proxy in `next.config.ts` for same-origin.
