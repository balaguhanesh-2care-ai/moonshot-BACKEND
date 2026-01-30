import logging
from pathlib import Path
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Header, HTTPException, Request

from config import AUDIO_FILE_PATH, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL
from services.ekascribe import transcribe_audio_files
from services.ekascribe_to_fhir import get_decoded_prescription
from services.scribe2fhir import emr_json_to_fhir_bundle, is_available as scribe2fhir_available
from services.supabase_client import insert_fhir_bundle

router = APIRouter()
log = logging.getLogger(__name__)


def _ensure_supabase() -> None:
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(
            status_code=503,
            detail="Supabase not configured (SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY or NEXT_PUBLIC_* equivalents)",
        )


async def _get_audio_tuples(request: Request) -> list[tuple[str, bytes]]:
    content_type = (request.headers.get("content-type") or "").lower()
    if "multipart/form-data" in content_type:
        form = await request.form()
        files = []
        for key in form.keys():
            field = form.get(key)
            if hasattr(field, "read"):
                content = await field.read()
                name = getattr(field, "filename", None) or key or "audio"
                files.append((name, content))
        if files:
            return files
    try:
        body = await request.json()
        if isinstance(body, dict):
            audio_url = body.get("audio_url") or body.get("audio_path")
            if audio_url and isinstance(audio_url, str) and audio_url.startswith(("http://", "https://")):
                async with httpx.AsyncClient() as client:
                    r = await client.get(audio_url, timeout=60.0)
                    r.raise_for_status()
                content = r.content
                name = Path(urlparse(audio_url).path).name or "audio"
                if not name or name == "/":
                    name = "audio.mp3"
                log.info("Fetched audio from URL: %s (%d bytes)", audio_url[:80], len(content))
                return [(name, content)]
            if body.get("audio_path"):
                path = Path(body["audio_path"])
                if path.is_file():
                    return [(path.name, path.read_bytes())]
                raise HTTPException(status_code=400, detail=f"Audio file not found: {body['audio_path']}")
    except HTTPException:
        raise
    except Exception:
        pass
    if AUDIO_FILE_PATH:
        s = AUDIO_FILE_PATH.strip()
        if s.startswith(("http://", "https://")):
            async with httpx.AsyncClient() as client:
                r = await client.get(s, timeout=60.0)
                r.raise_for_status()
            content = r.content
            name = Path(urlparse(s).path).name or "audio"
            if not name or name == "/":
                name = "audio.mp3"
            log.info("Using AUDIO_FILE_PATH (URL): %s (%d bytes)", s[:80], len(content))
            return [(name, content)]
        path = Path(s)
        if path.is_file():
            content = path.read_bytes()
            log.info("Using AUDIO_FILE_PATH (local): %s (%d bytes)", s, len(content))
            return [(path.name, content)]
        raise HTTPException(status_code=400, detail=f"Audio not found: AUDIO_FILE_PATH is not a valid URL or file path")
    raise HTTPException(
        status_code=400,
        detail="Set AUDIO_FILE_PATH (URL or path) in .env or send multipart file(s) or JSON with audio_url / audio_path",
    )


@router.post("/audio-to-fhir")
async def audio_to_fhir(
    request: Request,
    x_eka_scribe_api_token: str | None = Header(None, alias="X-EkaScribe-Api-Token"),
    x_eka_scribe_client_id: str | None = Header(None, alias="X-EkaScribe-Client-Id"),
    x_eka_scribe_client_id_alt: str | None = Header(None, alias="X-Eka-Scribe-Client-Id"),
    x_eka_scribe_client_secret: str | None = Header(None, alias="X-EkaScribe-Client-Secret"),
    x_eka_scribe_base_url: str | None = Header(None, alias="X-EkaScribe-Base-Url"),
    x_eka_api_token: str | None = Header(None, alias="X-Eka-Api-Token"),
    x_eka_client_id: str | None = Header(None, alias="X-Eka-Client-Id"),
    x_eka_client_secret: str | None = Header(None, alias="X-Eka-Client-Secret"),
    x_eka_base_url: str | None = Header(None, alias="X-Eka-Base-Url"),
):
    """
    Audio → Scribe → FHIR → Supabase. All Scribe keys from client (headers only; backend does not use server .env).
    Required: X-EkaScribe-Api-Token or (X-EkaScribe-Client-Id + X-EkaScribe-Client-Secret). Optional: X-EkaScribe-Base-Url.
    """
    log.info("Pipeline /audio-to-fhir started")
    if not scribe2fhir_available():
        raise HTTPException(status_code=503, detail="scribe2fhir SDK not available")
    _ensure_supabase()

    file_tuples = await _get_audio_tuples(request)
    total_bytes = sum(len(c) for _, c in file_tuples)
    log.info("Audio input: %d file(s), %d bytes total: %s", len(file_tuples), total_bytes, [n for n, _ in file_tuples])

    scribe_client_id = x_eka_scribe_client_id or x_eka_scribe_client_id_alt
    eka_auth = _eka_scribe_auth_from_headers(
        x_eka_scribe_api_token, scribe_client_id, x_eka_scribe_client_secret, x_eka_scribe_base_url,
        x_eka_api_token, x_eka_client_id, x_eka_client_secret, x_eka_base_url,
    )
    if not eka_auth:
        raise HTTPException(
            status_code=400,
            detail="Missing Scribe credentials: send X-EkaScribe-Api-Token or X-EkaScribe-Client-Id + X-EkaScribe-Client-Secret",
        )
    try:
        log.info("Calling EkaScribe (upload + init + poll)...")
        ekascribe_result = await transcribe_audio_files(file_tuples, eka_auth=eka_auth)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        log.exception("EkaScribe failed")
        detail = str(e)
        if getattr(e, "response", None) is not None:
            try:
                body = e.response.json()
                detail = body.get("message") or body.get("error") or body.get("detail") or detail
            except Exception:
                if e.response.text:
                    detail = e.response.text[:500]
        raise HTTPException(status_code=502, detail=f"EkaScribe error: {detail}")

    if not isinstance(ekascribe_result, dict):
        log.error("EkaScribe returned non-dict: %s", type(ekascribe_result).__name__)
        raise HTTPException(status_code=502, detail="EkaScribe returned invalid response shape")
    ekascribe_keys = list(ekascribe_result.keys())
    log.info("EkaScribe done. Response top-level keys: %s", ekascribe_keys)

    try:
        log.info("Converting EkaScribe JSON to FHIR bundle...")
        fhir_bundle = emr_json_to_fhir_bundle(ekascribe_result)
    except Exception as e:
        log.exception("scribe2fhir mapping failed")
        raise HTTPException(status_code=502, detail=f"scribe2fhir mapping error: {e}")

    if not isinstance(fhir_bundle, dict) or fhir_bundle.get("resourceType") != "Bundle":
        log.error("FHIR bundle invalid: resourceType=%s", fhir_bundle.get("resourceType") if isinstance(fhir_bundle, dict) else type(fhir_bundle).__name__)
        raise HTTPException(status_code=502, detail="scribe2fhir produced invalid FHIR Bundle")
    entry_count = len(fhir_bundle.get("entry") or [])
    log.info("FHIR bundle built: %d entries", entry_count)

    patient_id = None
    encounter_id = None
    txn_id = ekascribe_result.get("txn_id") or ekascribe_result.get("transaction_id") or ekascribe_result.get("id")
    if isinstance(fhir_bundle, dict):
        for entry in (fhir_bundle.get("entry") or []):
            res = entry.get("resource") if isinstance(entry, dict) else None
            if isinstance(res, dict):
                rt = res.get("resourceType")
                if rt == "Patient" and res.get("id"):
                    patient_id = res.get("id")
                if rt == "Encounter" and res.get("id"):
                    encounter_id = res.get("id")
                if patient_id and encounter_id:
                    break

    decoded_prescription = get_decoded_prescription(ekascribe_result)
    try:
        log.info("Inserting into Supabase (bundle + ekascribe_json + decoded_prescription)...")
        row = insert_fhir_bundle(
            fhir_bundle,
            ekascribe_json=ekascribe_result,
            decoded_prescription=decoded_prescription,
            patient_id=patient_id,
            encounter_id=encounter_id,
            txn_id=txn_id,
        )
    except Exception as e:
        log.exception("Supabase insert failed")
        raise HTTPException(status_code=503, detail=f"Database error: {e}")

    row_id = row.get("id")
    log.info("Pipeline done. DB row id=%s patient_id=%s encounter_id=%s", row_id, patient_id, encounter_id)

    return {
        "bundle": fhir_bundle,
        "db": {"id": row_id, "created_at": row.get("created_at")},
    }


def _auth_from_params(
    api_token: str | None,
    client_id: str | None,
    client_secret: str | None,
    base_url: str | None,
) -> dict | None:
    if api_token and api_token.strip():
        out = {"api_token": api_token.strip()}
        if base_url and base_url.strip():
            out["base_url"] = base_url.strip()
        return out
    if client_id and client_secret:
        out = {"client_id": client_id.strip(), "client_secret": client_secret.strip()}
        if base_url and base_url.strip():
            out["base_url"] = base_url.strip()
        return out
    return None


def _eka_scribe_auth_from_headers(
    x_scribe_token: str | None,
    x_scribe_client_id: str | None,
    x_scribe_client_secret: str | None,
    x_scribe_base_url: str | None,
    x_eka_api_token: str | None,
    x_eka_client_id: str | None,
    x_eka_client_secret: str | None,
    x_eka_base_url: str | None,
) -> dict | None:
    auth = _auth_from_params(x_scribe_token, x_scribe_client_id, x_scribe_client_secret, x_scribe_base_url)
    if auth:
        return auth
    return _auth_from_params(x_eka_api_token, x_eka_client_id, x_eka_client_secret, x_eka_base_url)


def _eka_emr_auth_from_headers(
    x_emr_token: str | None,
    x_emr_client_id: str | None,
    x_emr_client_secret: str | None,
    x_emr_base_url: str | None,
    x_eka_api_token: str | None,
    x_eka_client_id: str | None,
    x_eka_client_secret: str | None,
    x_eka_base_url: str | None,
) -> dict | None:
    auth = _auth_from_params(x_emr_token, x_emr_client_id, x_emr_client_secret, x_emr_base_url)
    if auth:
        return auth
    return _auth_from_params(x_eka_api_token, x_eka_client_id, x_eka_client_secret, x_eka_base_url)


@router.post("/audio-to-emr")
async def audio_to_emr(
    request: Request,
    x_pt_id: str = Header(..., alias="X-Pt-Id"),
    document_type: str = "ps",
    include_metadata: bool = False,
    x_eka_scribe_api_token: str | None = Header(None, alias="X-EkaScribe-Api-Token"),
    x_eka_scribe_client_id: str | None = Header(None, alias="X-EkaScribe-Client-Id"),
    x_eka_scribe_client_id_alt: str | None = Header(None, alias="X-Eka-Scribe-Client-Id"),
    x_eka_scribe_client_secret: str | None = Header(None, alias="X-EkaScribe-Client-Secret"),
    x_eka_scribe_base_url: str | None = Header(None, alias="X-EkaScribe-Base-Url"),
    x_eka_emr_api_token: str | None = Header(None, alias="X-EkaEmr-Api-Token"),
    x_eka_emr_client_id: str | None = Header(None, alias="X-EkaEmr-Client-Id"),
    x_eka_emr_client_secret: str | None = Header(None, alias="X-EkaEmr-Client-Secret"),
    x_eka_emr_base_url: str | None = Header(None, alias="X-EkaEmr-Base-Url"),
    x_eka_api_token: str | None = Header(None, alias="X-Eka-Api-Token"),
    x_eka_client_id: str | None = Header(None, alias="X-Eka-Client-Id"),
    x_eka_client_secret: str | None = Header(None, alias="X-Eka-Client-Secret"),
    x_eka_base_url: str | None = Header(None, alias="X-Eka-Base-Url"),
):
    """
    Single flow: Scribe audio → FHIR (Supabase) → push to EkaCare EMR.
    All keys from client (headers); backend does not use server .env for Scribe or EMR.
    Required: X-Pt-Id; X-EkaScribe-Api-Token (or Scribe client id+secret); X-EkaEmr-Api-Token or X-Eka-Client-Id + X-Eka-Client-Secret.
    """
    log.info("Pipeline /audio-to-emr started (X-Pt-Id=%s)", x_pt_id[:20] + "..." if len(x_pt_id) > 20 else x_pt_id)
    if not scribe2fhir_available():
        raise HTTPException(status_code=503, detail="scribe2fhir SDK not available")
    _ensure_supabase()

    file_tuples = await _get_audio_tuples(request)
    total_bytes = sum(len(c) for _, c in file_tuples)
    log.info("Audio input: %d file(s), %d bytes: %s", len(file_tuples), total_bytes, [n for n, _ in file_tuples])

    scribe_client_id = x_eka_scribe_client_id or x_eka_scribe_client_id_alt
    eka_scribe_auth = _eka_scribe_auth_from_headers(
        x_eka_scribe_api_token, scribe_client_id, x_eka_scribe_client_secret, x_eka_scribe_base_url,
        x_eka_api_token, x_eka_client_id, x_eka_client_secret, x_eka_base_url,
    )
    if not eka_scribe_auth:
        raise HTTPException(
            status_code=400,
            detail="Missing Scribe credentials: send X-EkaScribe-Api-Token or X-EkaScribe-Client-Id + X-EkaScribe-Client-Secret",
        )
    eka_emr_auth = _eka_emr_auth_from_headers(
        x_eka_emr_api_token, x_eka_emr_client_id, x_eka_emr_client_secret, x_eka_emr_base_url,
        x_eka_api_token, x_eka_client_id, x_eka_client_secret, x_eka_base_url,
    )
    if not eka_emr_auth:
        raise HTTPException(
            status_code=400,
            detail="Missing EMR credentials: send X-EkaEmr-Api-Token or X-Eka-Client-Id + X-Eka-Client-Secret",
        )
    try:
        log.info("Calling EkaScribe (upload + init + poll)...")
        ekascribe_result = await transcribe_audio_files(file_tuples, eka_auth=eka_scribe_auth)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        log.exception("EkaScribe failed")
        detail = str(e)
        if getattr(e, "response", None) is not None:
            try:
                body = e.response.json()
                detail = body.get("message") or body.get("error") or body.get("detail") or detail
            except Exception:
                if e.response.text:
                    detail = e.response.text[:500]
        raise HTTPException(status_code=502, detail=f"EkaScribe error: {detail}")

    if not isinstance(ekascribe_result, dict):
        log.error("EkaScribe returned non-dict: %s", type(ekascribe_result).__name__)
        raise HTTPException(status_code=502, detail="EkaScribe returned invalid response shape")

    try:
        fhir_bundle = emr_json_to_fhir_bundle(ekascribe_result)
    except Exception as e:
        log.exception("scribe2fhir mapping failed")
        raise HTTPException(status_code=502, detail=f"scribe2fhir mapping error: {e}")

    if not isinstance(fhir_bundle, dict) or fhir_bundle.get("resourceType") != "Bundle":
        log.error("FHIR bundle invalid: resourceType=%s", fhir_bundle.get("resourceType") if isinstance(fhir_bundle, dict) else type(fhir_bundle).__name__)
        raise HTTPException(status_code=502, detail="scribe2fhir produced invalid FHIR Bundle")

    patient_id = None
    encounter_id = None
    txn_id = ekascribe_result.get("txn_id") or ekascribe_result.get("transaction_id") or ekascribe_result.get("id")
    for entry in (fhir_bundle.get("entry") or []):
        res = entry.get("resource") if isinstance(entry, dict) else None
        if isinstance(res, dict):
            rt = res.get("resourceType")
            if rt == "Patient" and res.get("id"):
                patient_id = res.get("id")
            if rt == "Encounter" and res.get("id"):
                encounter_id = res.get("id")
            if patient_id and encounter_id:
                break

    decoded_prescription = get_decoded_prescription(ekascribe_result)
    try:
        row = insert_fhir_bundle(
            fhir_bundle,
            ekascribe_json=ekascribe_result,
            decoded_prescription=decoded_prescription,
            patient_id=patient_id,
            encounter_id=encounter_id,
            txn_id=txn_id,
        )
    except Exception as e:
        log.exception("Supabase insert failed")
        raise HTTPException(status_code=503, detail=f"Database error: {e}")

    row_id = row.get("id")
    log.info("Pipeline done. FHIR stored in Supabase (EkaCare docs push disabled).")

    return {
        "scribe": ekascribe_result,
        "bundle": fhir_bundle,
        "db": {"id": row_id, "created_at": row.get("created_at")},
    }
