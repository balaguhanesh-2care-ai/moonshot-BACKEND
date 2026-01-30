import logging
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

log = logging.getLogger(__name__)

backend_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=backend_dir / ".env")
load_dotenv(dotenv_path=backend_dir.parent / ".env")
load_dotenv()

# Legacy (fallback for both if EKASCRIBE_* / EKAEMR_* not set)
EKA_API_TOKEN = os.getenv("EKA_API_TOKEN", "").strip() or None
EKA_CLIENT_ID = os.getenv("EKA_CLIENT_ID", "").strip() or None
EKA_CLIENT_SECRET = os.getenv("EKA_CLIENT_SECRET", "").strip() or None
EKA_BASE_URL = os.getenv("EKA_BASE_URL", "").strip() or "https://api.eka.care"

# EkaScribe backup (final fallback so scribe never fails when set)
EKA_CLIENT_SCRIBE_SECRET = os.getenv("EKA_CLIENT_SCRIBE_SECRET", "").strip() or None
EKA_CLIENT_SCRIBE_CLIENT_ID = os.getenv("EKA_CLIENT_SCRIBE_CLIENT_ID", "").strip() or None

# EkaScribe (transcription)
EKASCRIBE_API_TOKEN = (
    os.getenv("EKASCRIBE_API_TOKEN", "").strip() or EKA_API_TOKEN or EKA_CLIENT_SCRIBE_SECRET
)
EKASCRIBE_CLIENT_ID = (
    os.getenv("EKASCRIBE_CLIENT_ID", "").strip() or EKA_CLIENT_ID or EKA_CLIENT_SCRIBE_CLIENT_ID
)
EKASCRIBE_CLIENT_SECRET = os.getenv("EKASCRIBE_CLIENT_SECRET", "").strip() or EKA_CLIENT_SECRET
EKASCRIBE_BASE_URL = os.getenv("EKASCRIBE_BASE_URL", "").strip() or EKA_BASE_URL

# Eka EMR (records, patient, ABDM, etc.)
EKAEMR_API_TOKEN = os.getenv("EKAEMR_API_TOKEN", "").strip() or EKA_API_TOKEN
EKAEMR_CLIENT_ID = os.getenv("EKAEMR_CLIENT_ID", "").strip() or EKA_CLIENT_ID
EKAEMR_CLIENT_SECRET = os.getenv("EKAEMR_CLIENT_SECRET", "").strip() or EKA_CLIENT_SECRET
EKAEMR_BASE_URL = os.getenv("EKAEMR_BASE_URL", "").strip() or EKA_BASE_URL

_scribe_token_cache: dict = {}
_emr_token_cache: dict = {}
_emr_connect_cache: dict = {}

SCRIBE_API_KEY = os.getenv("SCRIBE_API_KEY")
SCRIBE_CLIENT_ID = os.getenv("SCRIBE_CLIENT_ID")

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY")

AUDIO_FILE_PATH = os.getenv("AUDIO_FILE_PATH", "").strip() or None

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip() or None
GROQ_MODEL = os.getenv("GROQ_MODEL", "").strip() or "llama-3.3-70b-versatile"

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip() or None

CORS_ORIGINS_RAW = os.getenv("CORS_ORIGINS", "http://localhost:3000").strip()
CORS_ORIGINS = ["*"] if CORS_ORIGINS_RAW == "*" else [o.strip() for o in CORS_ORIGINS_RAW.split(",") if o.strip()] or ["http://localhost:3000"]
CORS_ALLOW_CREDENTIALS = CORS_ORIGINS != ["*"]


def validate_eka_scribe_config() -> None:
    if EKASCRIBE_API_TOKEN:
        return
    if EKASCRIBE_CLIENT_ID and EKASCRIBE_CLIENT_SECRET:
        return
    raise ValueError(
        "EkaScribe requires EKASCRIBE_API_TOKEN or (EKASCRIBE_CLIENT_ID + EKASCRIBE_CLIENT_SECRET), "
        "legacy EKA_*, or backup EKA_CLIENT_SCRIBE_SECRET / EKA_CLIENT_SCRIBE_CLIENT_ID"
    )


def validate_eka_emr_config() -> None:
    if EKAEMR_API_TOKEN:
        return
    if EKAEMR_CLIENT_ID and EKAEMR_CLIENT_SECRET:
        return
    raise ValueError(
        "Eka EMR requires EKAEMR_API_TOKEN or (EKAEMR_CLIENT_ID + EKAEMR_CLIENT_SECRET), or legacy EKA_*"
    )


def _fetch_connect_token_scribe() -> str:
    url = f"{EKASCRIBE_BASE_URL.rstrip('/')}/connect-auth/v1/account/login"
    with httpx.Client() as client:
        r = client.post(
            url,
            json={"client_id": EKASCRIBE_CLIENT_ID, "client_secret": EKASCRIBE_CLIENT_SECRET},
            headers={"Content-Type": "application/json"},
            timeout=15.0,
        )
    r.raise_for_status()
    data = r.json()
    token = data.get("access_token")
    if not token:
        raise ValueError("Connect Login response missing access_token")
    expires_in = int(data.get("expires_in", 1800)) - 60
    _scribe_token_cache["access_token"] = token
    _scribe_token_cache["expires_at"] = time.time() + expires_in
    log.info("EkaScribe Connect Login OK, token cached (%ds)", expires_in)
    return token


def _fetch_connect_token_from_params(client_id: str, client_secret: str, base_url: str) -> str:
    url = f"{base_url.rstrip('/')}/connect-auth/v1/account/login"
    with httpx.Client() as client:
        r = client.post(
            url,
            json={"client_id": client_id, "client_secret": client_secret},
            headers={"Content-Type": "application/json"},
            timeout=15.0,
        )
    r.raise_for_status()
    data = r.json()
    token = data.get("access_token")
    if not token:
        raise ValueError("Connect Login response missing access_token")
    return token


def get_eka_scribe_headers() -> dict[str, str]:
    validate_eka_scribe_config()
    if EKASCRIBE_CLIENT_ID and EKASCRIBE_CLIENT_SECRET:
        now = time.time()
        if not _scribe_token_cache.get("access_token") or (_scribe_token_cache.get("expires_at") or 0) <= now:
            token = _fetch_connect_token_scribe()
        else:
            token = _scribe_token_cache["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {"Authorization": f"Bearer {EKASCRIBE_API_TOKEN}"}


def get_eka_scribe_headers_from_params(
    *,
    api_token: str | None = None,
    client_id: str | None = None,
    client_secret: str | None = None,
    base_url: str | None = None,
) -> tuple[dict[str, str], str]:
    base = (base_url or EKASCRIBE_BASE_URL or "https://api.eka.care").rstrip("/")
    if api_token:
        return {"Authorization": f"Bearer {api_token.strip()}"}, base
    if client_id and client_secret:
        cid, csec = client_id.strip(), client_secret.strip()
        if not cid or not csec:
            raise ValueError("client_id and client_secret must be non-empty")
        cache_key = ("scribe", cid, csec, base)
        now = time.time()
        cached = _emr_connect_cache.get(cache_key)
        if cached and (cached.get("expires_at") or 0) > now:
            return {"Authorization": f"Bearer {cached['access_token']}"}, base
        token = _fetch_connect_token_from_params(cid, csec, base)
        _emr_connect_cache[cache_key] = {"access_token": token, "expires_at": time.time() + 1800 - 60}
        return {"Authorization": f"Bearer {token}"}, base
    return get_eka_scribe_headers(), base


def get_eka_emr_headers() -> dict[str, str]:
    validate_eka_emr_config()
    if EKAEMR_CLIENT_ID and EKAEMR_CLIENT_SECRET:
        url = f"{EKAEMR_BASE_URL.rstrip('/')}/connect-auth/v1/account/login"
        now = time.time()
        cache_key = ("emr", EKAEMR_CLIENT_ID, EKAEMR_CLIENT_SECRET, EKAEMR_BASE_URL)
        cached = _emr_connect_cache.get(cache_key)
        if not cached or (cached.get("expires_at") or 0) <= now:
            token = _fetch_connect_token_from_params(EKAEMR_CLIENT_ID, EKAEMR_CLIENT_SECRET, EKAEMR_BASE_URL)
            _emr_connect_cache[cache_key] = {"access_token": token, "expires_at": time.time() + 1800 - 60}
        else:
            token = cached["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {"Authorization": f"Bearer {EKAEMR_API_TOKEN}"}


def get_eka_emr_headers_from_params(
    *,
    api_token: str | None = None,
    client_id: str | None = None,
    client_secret: str | None = None,
    base_url: str | None = None,
) -> tuple[dict[str, str], str]:
    base = (base_url or EKAEMR_BASE_URL or "https://api.eka.care").rstrip("/")
    if api_token:
        return {"Authorization": f"Bearer {api_token.strip()}"}, base
    if client_id and client_secret:
        cid, csec = client_id.strip(), client_secret.strip()
        if not cid or not csec:
            raise ValueError("client_id and client_secret must be non-empty")
        cache_key = ("emr", cid, csec, base)
        now = time.time()
        cached = _emr_connect_cache.get(cache_key)
        if cached and (cached.get("expires_at") or 0) > now:
            return {"Authorization": f"Bearer {cached['access_token']}"}, base
        token = _fetch_connect_token_from_params(cid, csec, base)
        _emr_connect_cache[cache_key] = {"access_token": token, "expires_at": time.time() + 1800 - 60}
        return {"Authorization": f"Bearer {token}"}, base
    return get_eka_emr_headers(), base


def validate_eka_config() -> None:
    validate_eka_scribe_config()
    validate_eka_emr_config()
