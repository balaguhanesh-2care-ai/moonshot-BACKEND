import logging
from pathlib import Path
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Header, HTTPException, Request

from config import AUDIO_FILE_PATH, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL
from services.ekascribe import EkaScribeError, transcribe_audio_files
from services.ekascribe_to_fhir import get_decoded_prescription
from services.scribe2fhir import emr_json_to_fhir_bundle, is_available as scribe2fhir_available
from services.supabase_client import insert_fhir_bundle

router = APIRouter()
log = logging.getLogger(__name__)


def _supabase_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)


FALLBACK_BUNDLE: dict = {
    "resourceType": "Bundle",
    "type": "document",
    "entry": [],
}

FALLBACK_SCRIBE: dict = {
    "status": "fallback",
    "txn_id": "fallback",
    "data": {},
    "error_fallback": True,
}


def _pipeline_response(
    *,
    ok: bool,
    bundle: dict | None,
    db: dict | None,
    errors: list[dict],
    scribe: dict | None = None,
) -> dict:
    out: dict = {
        "ok": ok,
        "bundle": bundle if bundle is not None else FALLBACK_BUNDLE,
        "db": db,
        "errors": errors,
    }
    out["scribe"] = scribe if scribe is not None else FALLBACK_SCRIBE
    return out


def _try_store_fallback(bundle: dict, scribe: dict, errors: list[dict]) -> dict | None:
    if not _supabase_configured():
        return None
    try:
        row = insert_fhir_bundle(
            bundle,
            ekascribe_json=scribe,
            decoded_prescription=None,
            patient_id=None,
            encounter_id=None,
            txn_id=scribe.get("txn_id") or "fallback",
        )
        return {"id": row.get("id"), "created_at": row.get("created_at")}
    except Exception as e:
        log.warning("Fallback DB insert failed: %s", e)
        errors.append({"step": "db", "message": str(e)})
        return None


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
    errors: list[dict] = []
    ekascribe_result: dict | None = None
    fhir_bundle: dict | None = None
    row: dict | None = None

    if not scribe2fhir_available():
        errors.append({"step": "config", "message": "scribe2fhir SDK not available"})
        db_fallback = _try_store_fallback(FALLBACK_BUNDLE, FALLBACK_SCRIBE, errors) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fallback, errors=errors, scribe=FALLBACK_SCRIBE)

    try:
        file_tuples = await _get_audio_tuples(request)
    except HTTPException as e:
        errors.append({"step": "input", "message": e.detail or str(e)})
        db_fallback = _try_store_fallback(FALLBACK_BUNDLE, FALLBACK_SCRIBE, errors) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fallback, errors=errors, scribe=FALLBACK_SCRIBE)
    except Exception as e:
        log.exception("Get audio failed")
        errors.append({"step": "input", "message": str(e)})
        db_fallback = _try_store_fallback(FALLBACK_BUNDLE, FALLBACK_SCRIBE, errors) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fallback, errors=errors, scribe=FALLBACK_SCRIBE)

    total_bytes = sum(len(c) for _, c in file_tuples)
    log.info("Audio input: %d file(s), %d bytes total: %s", len(file_tuples), total_bytes, [n for n, _ in file_tuples])

    scribe_client_id = x_eka_scribe_client_id or x_eka_scribe_client_id_alt
    eka_auth = _eka_scribe_auth_from_headers(
        x_eka_scribe_api_token, scribe_client_id, x_eka_scribe_client_secret, x_eka_scribe_base_url,
        x_eka_api_token, x_eka_client_id, x_eka_client_secret, x_eka_base_url,
    )
    if not eka_auth:
        errors.append({"step": "auth", "message": "Missing Scribe credentials"})
        db_fallback = _try_store_fallback(FALLBACK_BUNDLE, FALLBACK_SCRIBE, errors) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fallback, errors=errors, scribe=FALLBACK_SCRIBE)

    try:
        log.info("Calling EkaScribe (upload + init + poll)...")
        ekascribe_result = await transcribe_audio_files(file_tuples, eka_auth=eka_auth)
    except ValueError as e:
        errors.append({"step": "ekascribe", "message": str(e)})
        db_fallback = _try_store_fallback(FALLBACK_BUNDLE, FALLBACK_SCRIBE, errors) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fallback, errors=errors, scribe=FALLBACK_SCRIBE)
    except TimeoutError as e:
        errors.append({"step": "ekascribe", "message": str(e)})
        db_fallback = _try_store_fallback(FALLBACK_BUNDLE, FALLBACK_SCRIBE, errors) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fallback, errors=errors, scribe=FALLBACK_SCRIBE)
    except EkaScribeError as e:
        log.warning("EkaScribe failed: %s", e.message)
        errors.append({"step": "ekascribe", "message": e.message})
        scribe_fb = ekascribe_result if isinstance(ekascribe_result, dict) else FALLBACK_SCRIBE
        db_fallback = _try_store_fallback(FALLBACK_BUNDLE, scribe_fb, errors) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fallback, errors=errors, scribe=scribe_fb)
    except Exception as e:
        log.exception("EkaScribe failed")
        detail = str(e)
        if getattr(e, "response", None) is not None:
            try:
                body = e.response.json()
                detail = body.get("message") or body.get("error") or body.get("detail") or detail
            except Exception:
                if getattr(e.response, "text", None):
                    detail = e.response.text[:500]
        errors.append({"step": "ekascribe", "message": detail})
        scribe_fb = ekascribe_result if isinstance(ekascribe_result, dict) else FALLBACK_SCRIBE
        db_fallback = _try_store_fallback(FALLBACK_BUNDLE, scribe_fb, errors) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fallback, errors=errors, scribe=scribe_fb)

    if not isinstance(ekascribe_result, dict):
        log.error("EkaScribe returned non-dict: %s", type(ekascribe_result).__name__)
        errors.append({"step": "ekascribe", "message": "Invalid response shape"})
        db_fallback = _try_store_fallback(FALLBACK_BUNDLE, FALLBACK_SCRIBE, errors) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fallback, errors=errors, scribe=FALLBACK_SCRIBE)
    log.info("EkaScribe done. Response top-level keys: %s", list(ekascribe_result.keys()))

    try:
        log.info("Converting EkaScribe JSON to FHIR bundle...")
        fhir_bundle = emr_json_to_fhir_bundle(ekascribe_result)
    except Exception as e:
        log.exception("scribe2fhir mapping failed")
        errors.append({"step": "fhir", "message": str(e)})
        db_fallback = _try_store_fallback(FALLBACK_BUNDLE, ekascribe_result, errors) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fallback, errors=errors, scribe=ekascribe_result)

    if not isinstance(fhir_bundle, dict) or fhir_bundle.get("resourceType") != "Bundle":
        log.error("FHIR bundle invalid")
        errors.append({"step": "fhir", "message": "Invalid FHIR Bundle"})
        db_fallback = _try_store_fallback(FALLBACK_BUNDLE, ekascribe_result, errors) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fallback, errors=errors, scribe=ekascribe_result)
    log.info("FHIR bundle built: %d entries", len(fhir_bundle.get("entry") or []))

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
        errors.append({"step": "db", "message": str(e)})
        return _pipeline_response(ok=False, bundle=fhir_bundle, db=None, errors=errors, scribe=ekascribe_result)

    log.info("Pipeline done. DB row id=%s patient_id=%s encounter_id=%s", row.get("id"), patient_id, encounter_id)
    return _pipeline_response(
        ok=True,
        bundle=fhir_bundle,
        db={"id": row.get("id"), "created_at": row.get("created_at")},
        errors=[],
        scribe=ekascribe_result,
    )


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
    errors_emr: list[dict] = []
    ekascribe_result_emr: dict | None = None
    fhir_bundle_emr: dict | None = None
    row_emr: dict | None = None

    if not scribe2fhir_available():
        errors_emr.append({"step": "config", "message": "scribe2fhir SDK not available"})
        db_fb = _try_store_fallback(FALLBACK_BUNDLE, FALLBACK_SCRIBE, errors_emr) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fb, errors=errors_emr, scribe=FALLBACK_SCRIBE)

    try:
        file_tuples = await _get_audio_tuples(request)
    except HTTPException as e:
        errors_emr.append({"step": "input", "message": e.detail or str(e)})
        db_fb = _try_store_fallback(FALLBACK_BUNDLE, FALLBACK_SCRIBE, errors_emr) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fb, errors=errors_emr, scribe=FALLBACK_SCRIBE)
    except Exception as e:
        log.exception("Get audio failed")
        errors_emr.append({"step": "input", "message": str(e)})
        db_fb = _try_store_fallback(FALLBACK_BUNDLE, FALLBACK_SCRIBE, errors_emr) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fb, errors=errors_emr, scribe=FALLBACK_SCRIBE)

    total_bytes = sum(len(c) for _, c in file_tuples)
    log.info("Audio input: %d file(s), %d bytes: %s", len(file_tuples), total_bytes, [n for n, _ in file_tuples])

    scribe_client_id = x_eka_scribe_client_id or x_eka_scribe_client_id_alt
    eka_scribe_auth = _eka_scribe_auth_from_headers(
        x_eka_scribe_api_token, scribe_client_id, x_eka_scribe_client_secret, x_eka_scribe_base_url,
        x_eka_api_token, x_eka_client_id, x_eka_client_secret, x_eka_base_url,
    )
    if not eka_scribe_auth:
        errors_emr.append({"step": "auth", "message": "Missing Scribe credentials"})
        db_fb = _try_store_fallback(FALLBACK_BUNDLE, FALLBACK_SCRIBE, errors_emr) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fb, errors=errors_emr, scribe=FALLBACK_SCRIBE)
    eka_emr_auth = _eka_emr_auth_from_headers(
        x_eka_emr_api_token, x_eka_emr_client_id, x_eka_emr_client_secret, x_eka_emr_base_url,
        x_eka_api_token, x_eka_client_id, x_eka_client_secret, x_eka_base_url,
    )
    if not eka_emr_auth:
        errors_emr.append({"step": "auth", "message": "Missing EMR credentials"})
        db_fb = _try_store_fallback(FALLBACK_BUNDLE, FALLBACK_SCRIBE, errors_emr) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fb, errors=errors_emr, scribe=FALLBACK_SCRIBE)

    try:
        log.info("Calling EkaScribe (upload + init + poll)...")
        ekascribe_result_emr = await transcribe_audio_files(file_tuples, eka_auth=eka_scribe_auth)
    except ValueError as e:
        errors_emr.append({"step": "ekascribe", "message": str(e)})
        db_fb = _try_store_fallback(FALLBACK_BUNDLE, FALLBACK_SCRIBE, errors_emr) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fb, errors=errors_emr, scribe=FALLBACK_SCRIBE)
    except TimeoutError as e:
        errors_emr.append({"step": "ekascribe", "message": str(e)})
        db_fb = _try_store_fallback(FALLBACK_BUNDLE, FALLBACK_SCRIBE, errors_emr) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fb, errors=errors_emr, scribe=FALLBACK_SCRIBE)
    except EkaScribeError as e:
        log.warning("EkaScribe failed: %s", e.message)
        errors_emr.append({"step": "ekascribe", "message": e.message})
        scribe_fb = ekascribe_result_emr if isinstance(ekascribe_result_emr, dict) else FALLBACK_SCRIBE
        db_fb = _try_store_fallback(FALLBACK_BUNDLE, scribe_fb, errors_emr) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fb, errors=errors_emr, scribe=scribe_fb)
    except Exception as e:
        log.exception("EkaScribe failed")
        detail = str(e)
        if getattr(e, "response", None) is not None:
            try:
                body = e.response.json()
                detail = body.get("message") or body.get("error") or body.get("detail") or detail
            except Exception:
                if getattr(e.response, "text", None):
                    detail = e.response.text[:500]
        errors_emr.append({"step": "ekascribe", "message": detail})
        scribe_fb = ekascribe_result_emr if isinstance(ekascribe_result_emr, dict) else FALLBACK_SCRIBE
        db_fb = _try_store_fallback(FALLBACK_BUNDLE, scribe_fb, errors_emr) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fb, errors=errors_emr, scribe=scribe_fb)

    if not isinstance(ekascribe_result_emr, dict):
        log.error("EkaScribe returned non-dict: %s", type(ekascribe_result_emr).__name__)
        errors_emr.append({"step": "ekascribe", "message": "Invalid response shape"})
        db_fb = _try_store_fallback(FALLBACK_BUNDLE, FALLBACK_SCRIBE, errors_emr) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fb, errors=errors_emr, scribe=FALLBACK_SCRIBE)

    try:
        fhir_bundle_emr = emr_json_to_fhir_bundle(ekascribe_result_emr)
    except Exception as e:
        log.exception("scribe2fhir mapping failed")
        errors_emr.append({"step": "fhir", "message": str(e)})
        db_fb = _try_store_fallback(FALLBACK_BUNDLE, ekascribe_result_emr, errors_emr) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fb, errors=errors_emr, scribe=ekascribe_result_emr)

    if not isinstance(fhir_bundle_emr, dict) or fhir_bundle_emr.get("resourceType") != "Bundle":
        log.error("FHIR bundle invalid")
        errors_emr.append({"step": "fhir", "message": "Invalid FHIR Bundle"})
        db_fb = _try_store_fallback(FALLBACK_BUNDLE, ekascribe_result_emr, errors_emr) if _supabase_configured() else None
        return _pipeline_response(ok=False, bundle=FALLBACK_BUNDLE, db=db_fb, errors=errors_emr, scribe=ekascribe_result_emr)

    patient_id = None
    encounter_id = None
    txn_id = ekascribe_result_emr.get("txn_id") or ekascribe_result_emr.get("transaction_id") or ekascribe_result_emr.get("id")
    for entry in (fhir_bundle_emr.get("entry") or []):
        res = entry.get("resource") if isinstance(entry, dict) else None
        if isinstance(res, dict):
            rt = res.get("resourceType")
            if rt == "Patient" and res.get("id"):
                patient_id = res.get("id")
            if rt == "Encounter" and res.get("id"):
                encounter_id = res.get("id")
            if patient_id and encounter_id:
                break

    decoded_prescription = get_decoded_prescription(ekascribe_result_emr)
    try:
        row_emr = insert_fhir_bundle(
            fhir_bundle_emr,
            ekascribe_json=ekascribe_result_emr,
            decoded_prescription=decoded_prescription,
            patient_id=patient_id,
            encounter_id=encounter_id,
            txn_id=txn_id,
        )
    except Exception as e:
        log.exception("Supabase insert failed")
        errors_emr.append({"step": "db", "message": str(e)})
        return _pipeline_response(ok=False, bundle=fhir_bundle_emr, db=None, errors=errors_emr, scribe=ekascribe_result_emr)

    log.info("Pipeline done. FHIR stored in Supabase (EkaCare docs push disabled).")
    return _pipeline_response(
        ok=True,
        bundle=fhir_bundle_emr,
        db={"id": row_emr.get("id"), "created_at": row_emr.get("created_at")},
        errors=[],
        scribe=ekascribe_result_emr,
    )
