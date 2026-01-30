# Moonshot Backend – Deployment

## Deployment readiness

- **Health**: `GET /health` returns `{"status":"ok"}`.
- **CORS**: Driven by `CORS_ORIGINS`; set to your frontend origin(s) in production. Only your frontend calls the backend (via Next.js server or directly); no extra origins needed.
- **Pipeline**: Audio → Scribe → FHIR → Supabase (EkaCare docs push disabled).

## Environment variables

### Required for pipeline (audio → FHIR → Supabase)

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Supabase project URL (or `NEXT_PUBLIC_SUPABASE_URL`) |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (or `NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY`) |

Pipeline auth is sent by the **frontend** in request headers (EkaScribe token/client id+secret). Backend does not need Eka env vars for pipeline if the Next app forwards them.

### Optional (backend fallback / other features)

| Variable | Description |
|----------|-------------|
| `EKA_API_TOKEN` | Legacy Eka API token (fallback for Scribe/EMR) |
| `EKA_CLIENT_ID` | Legacy Eka client id |
| `EKA_CLIENT_SECRET` | Legacy Eka client secret |
| `EKA_BASE_URL` | Eka API base (default `https://api.eka.care`) |
| `EKA_CLIENT_SCRIBE_SECRET` | EkaScribe secret (fallback) |
| `EKA_CLIENT_SCRIBE_CLIENT_ID` | EkaScribe client id (fallback) |
| `EKASCRIBE_API_TOKEN` | EkaScribe API token |
| `EKASCRIBE_CLIENT_ID` | EkaScribe client id |
| `EKASCRIBE_CLIENT_SECRET` | EkaScribe client secret |
| `EKASCRIBE_BASE_URL` | EkaScribe base URL |
| `EKAEMR_API_TOKEN` | Eka EMR API token |
| `EKAEMR_CLIENT_ID` | Eka EMR client id |
| `EKAEMR_CLIENT_SECRET` | Eka EMR client secret |
| `EKAEMR_BASE_URL` | Eka EMR base URL |
| `AUDIO_FILE_PATH` | Optional local file path or URL for pipeline input |
| `GROQ_API_KEY` | For agent (LangGraph) |
| `GROQ_MODEL` | Groq model (default `llama-3.3-70b-versatile`) |
| `TAVILY_API_KEY` | For agent (Tavily search) |
| `SCRIBE_API_KEY` | Alternative scribe API key |
| `SCRIBE_CLIENT_ID` | Alternative scribe client id |

### CORS (production)

| Variable | Description |
|----------|-------------|
| `CORS_ORIGINS` | Comma-separated allowed origins. Default `http://localhost:3000`. Set to `*` to allow all origins (credentials disabled per CORS spec). Or list origins, e.g. `https://your-app.vercel.app`. |

Allow all origins in prod:

```bash
CORS_ORIGINS=*
```

Specific origins:

```bash
CORS_ORIGINS=https://your-frontend.vercel.app,https://app.yourdomain.com
```

## scribe2fhir (required for pipeline)

The pipeline needs the **scribe2fhir** package. It is a local path dependency at `scribe2fhir/python`. You must have that folder in the repo at build time or the pipeline returns **503 "scribe2fhir SDK not available"** in production.

### Option A: Git submodule (if scribe2fhir is a separate repo)

From repo root:

```bash
git submodule add <URL-of-scribe2fhir-repo> scribe2fhir
```

The repo layout must expose the Python package at `scribe2fhir/python` (i.e. either the repo root is the package and you add it as `scribe2fhir` with a `python` subdir, or the repo has a `python` folder at top level—adjust the path in `pyproject.toml` `[tool.uv.sources]` if different).

Then in **Vercel** → Project → Settings → Git → enable **Include Git Submodules**. Redeploy so the build clones the submodule and `uv` can install from `scribe2fhir/python`.

### Option B: Vendor the package

Copy the scribe2fhir Python package into this repo so the path `scribe2fhir/python` exists (e.g. clone the scribe2fhir repo and copy its package folder into `scribe2fhir/python`). Commit and push. No submodule or Vercel setting needed.

### If you cannot add scribe2fhir

Remove `scribe2fhir` and `[tool.uv.sources]` from `pyproject.toml`, run `uv lock`, and redeploy. The app will start but pipeline endpoints will return 503 until scribe2fhir is available.

---

## Python dependencies (pyproject.toml)

- fastapi
- uvicorn[standard]
- httpx
- requests
- python-multipart
- python-dotenv
- supabase
- reportlab
- langgraph>=0.2.0
- langchain-core>=0.3.0
- langchain-groq>=0.2.0
- scribe2fhir (local path: `scribe2fhir/python`)

## Run for production

From repo root (moonshot-backend), with venv that has `scribe2fhir` on path:

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

Or with a process manager (e.g. gunicorn with uvicorn worker):

```bash
uv run gunicorn main:app -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## Frontend (Next.js) requirement

Set `PIPELINE_BASE_URL` to this backend’s public URL, e.g. `https://api.yourdomain.com`, so the Next.js API route can proxy pipeline requests to the backend.
