import asyncio
import uuid
from typing import Any

import httpx

from config import get_eka_headers

EKA_BASE = "https://api.eka.care"
FILE_UPLOAD_URL = f"{EKA_BASE}/v1/file-upload"
INIT_URL_TEMPLATE = f"{EKA_BASE}/voice/api/v2/transaction/init/{{txn_id}}"
STATUS_URL_TEMPLATE = f"{EKA_BASE}/voice/api/v3/status/{{txn_id}}"

POLL_INTERVAL_SEC = 3
MAX_POLL_ATTEMPTS = 120


async def get_presigned_url(txn_id: str) -> dict[str, Any]:
    params = {"action": "ekascribe-v2", "txn_id": txn_id}
    async with httpx.AsyncClient() as client:
        r = await client.post(
            FILE_UPLOAD_URL,
            params=params,
            headers=get_eka_headers(),
            timeout=30.0,
        )
        r.raise_for_status()
        return r.json()


async def upload_to_s3(
    upload_data: dict[str, Any],
    folder_path: str,
    file_content: bytes,
    filename: str,
) -> None:
    url = upload_data["url"]
    fields = dict(upload_data["fields"])
    fields["key"] = folder_path + filename
    form_data = list(fields.items())
    files = {"file": (filename, file_content)}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, data=form_data, files=files, timeout=60.0)
        r.raise_for_status()


async def init_transaction(
    txn_id: str,
    batch_s3_url: str,
    client_generated_files: list[str],
    *,
    mode: str = "dictation",
    transfer: str = "non-vaded",
    model_type: str = "pro",
) -> dict[str, Any]:
    body = {
        "mode": mode,
        "transfer": transfer,
        "batch_s3_url": batch_s3_url,
        "client_generated_files": client_generated_files,
        "model_type": model_type,
        "input_language": ["en-IN"],
        "output_language": "en-IN",
        "speciality": "general_medicine",
        "output_format_template": [
            {"template_id": "eka_emr_template", "codification_needed": False}
        ],
    }
    url = INIT_URL_TEMPLATE.format(txn_id=txn_id)
    async with httpx.AsyncClient() as client:
        r = await client.post(
            url,
            json=body,
            headers={**get_eka_headers(), "Content-Type": "application/json"},
            timeout=30.0,
        )
        r.raise_for_status()
        return r.json()


async def get_status(txn_id: str) -> tuple[int, dict[str, Any]]:
    url = STATUS_URL_TEMPLATE.format(txn_id=txn_id)
    async with httpx.AsyncClient() as client:
        r = await client.get(
            url,
            headers=get_eka_headers(),
            timeout=30.0,
        )
        return r.status_code, r.json() if r.content else {}


async def transcribe_audio_files(
    files: list[tuple[str, bytes]],
) -> dict[str, Any]:
    if not files:
        raise ValueError("At least one file required")
    txn_id = f"txn_{uuid.uuid4().hex[:12]}"
    headers = get_eka_headers()
    async with httpx.AsyncClient() as client:
        r = await client.post(
            FILE_UPLOAD_URL,
            params={"action": "ekascribe-v2", "txn_id": txn_id},
            headers=headers,
            timeout=30.0,
        )
        r.raise_for_status()
        presigned = r.json()
    upload_data = presigned["uploadData"]
    folder_path = presigned["folderPath"]
    filenames = []
    for filename, content in files:
        await upload_to_s3(upload_data, folder_path, content, filename)
        filenames.append(filename)
    batch_s3_url = upload_data["url"].rstrip("/") + "/" + folder_path
    await init_transaction(txn_id, batch_s3_url, filenames)
    for _ in range(MAX_POLL_ATTEMPTS):
        status_code, data = await get_status(txn_id)
        if status_code == 200:
            return data
        if status_code == 206:
            return data
        if status_code != 202:
            raise RuntimeError(f"EkaScribe status {status_code}: {data}")
        await asyncio.sleep(POLL_INTERVAL_SEC)
    raise TimeoutError("EkaScribe transcription did not complete in time")
