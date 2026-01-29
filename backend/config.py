import os
from pathlib import Path

from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=backend_dir / ".env")
load_dotenv(dotenv_path=backend_dir.parent / ".env")
load_dotenv()

EKA_API_TOKEN = os.getenv("EKA_API_TOKEN")
EKA_CLIENT_ID = os.getenv("EKA_CLIENT_ID")
EKA_CLIENT_SECRET = os.getenv("EKA_CLIENT_SECRET")

SCRIBE_API_KEY = os.getenv("SCRIBE_API_KEY")
SCRIBE_CLIENT_ID = os.getenv("SCRIBE_CLIENT_ID")


def validate_eka_config() -> None:
    if not EKA_API_TOKEN:
        raise ValueError("EKA_API_TOKEN is required for EkaScribe")


def get_eka_headers() -> dict[str, str]:
    validate_eka_config()
    return {"Authorization": f"Bearer {EKA_API_TOKEN}"}
