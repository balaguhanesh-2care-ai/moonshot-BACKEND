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

EKA_API_TOKEN = os.getenv("EKA_API_TOKEN", "").strip() or None
EKA_CLIENT_ID = os.getenv("EKA_CLIENT_ID", "").strip() or None
EKA_CLIENT_SECRET = os.getenv("EKA_CLIENT_SECRET", "").strip() or None

CONNECT_LOGIN_URL = "https://api.eka.care/connect-auth/v1/account/login"
_eka_token_cache: dict = {}

SCRIBE_API_KEY = os.getenv("SCRIBE_API_KEY")
SCRIBE_CLIENT_ID = os.getenv("SCRIBE_CLIENT_ID")

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY")

AUDIO_FILE_PATH = os.getenv("AUDIO_FILE_PATH", "").strip() or None


def validate_eka_config() -> None:
    if EKA_API_TOKEN:
        return
    if EKA_CLIENT_ID and EKA_CLIENT_SECRET:
        return
    raise ValueError(
        "EkaScribe requires either EKA_API_TOKEN or both EKA_CLIENT_ID and EKA_CLIENT_SECRET (Connect Login)"
    )


def _fetch_connect_token() -> str:
    with httpx.Client() as client:
        r = client.post(
            CONNECT_LOGIN_URL,
            json={"client_id": EKA_CLIENT_ID, "client_secret": EKA_CLIENT_SECRET},
            headers={"Content-Type": "application/json"},
            timeout=15.0,
        )
    r.raise_for_status()
    data = r.json()
    token = data.get("access_token")
    if not token:
        raise ValueError("Connect Login response missing access_token")
    expires_in = int(data.get("expires_in", 1800)) - 60
    _eka_token_cache["access_token"] = token
    _eka_token_cache["expires_at"] = time.time() + expires_in
    log.info("Connect Login OK, access_token cached (expires in %ds)", expires_in)
    return token


def get_eka_headers() -> dict[str, str]:
    validate_eka_config()
    if EKA_CLIENT_ID and EKA_CLIENT_SECRET:
        now = time.time()
        if not _eka_token_cache.get("access_token") or (_eka_token_cache.get("expires_at") or 0) <= now:
            token = _fetch_connect_token()
        else:
            token = _eka_token_cache["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {"Authorization": f"Bearer {EKA_API_TOKEN}"}
