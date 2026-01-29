import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from config import AUDIO_FILE_PATH, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL
from services.ekascribe import transcribe_audio_files
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
        if isinstance(body, dict) and body.get("audio_path"):
            path = Path(body["audio_path"])
            if not path.is_file():
                raise HTTPException(status_code=400, detail=f"Audio file not found: {body['audio_path']}")
            return [(path.name, path.read_bytes())]
    except HTTPException:
        raise
    except Exception:
        pass
    if AUDIO_FILE_PATH:
        path = Path(AUDIO_FILE_PATH)
        if path.is_file():
            content = path.read_bytes()
            log.info("Using AUDIO_FILE_PATH: %s (%d bytes)", AUDIO_FILE_PATH, len(content))
            return [(path.name, content)]
        raise HTTPException(status_code=400, detail=f"Audio file not found at AUDIO_FILE_PATH: {AUDIO_FILE_PATH}")
    raise HTTPException(
        status_code=400,
        detail="Set AUDIO_FILE_PATH in .env or provide multipart file(s) or JSON body with audio_path",
    )


@router.post("/audio-to-fhir")
async def audio_to_fhir(request: Request):
    log.info("Pipeline /audio-to-fhir started")
    if not scribe2fhir_available():
        raise HTTPException(status_code=503, detail="scribe2fhir SDK not available")
    _ensure_supabase()

    file_tuples = await _get_audio_tuples(request)
    total_bytes = sum(len(c) for _, c in file_tuples)
    log.info("Audio input: %d file(s), %d bytes total: %s", len(file_tuples), total_bytes, [n for n, _ in file_tuples])

    try:
        log.info("Calling EkaScribe (upload + init + poll)...")
        ekascribe_result = await transcribe_audio_files(file_tuples)
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

    ekascribe_keys = list(ekascribe_result.keys()) if isinstance(ekascribe_result, dict) else []
    log.info("EkaScribe done. Response top-level keys: %s", ekascribe_keys)

    try:
        log.info("Converting EkaScribe JSON to FHIR bundle...")
        fhir_bundle = emr_json_to_fhir_bundle(ekascribe_result)
    except Exception as e:
        log.exception("scribe2fhir mapping failed")
        raise HTTPException(status_code=502, detail=f"scribe2fhir mapping error: {e}")

    entry_count = len(fhir_bundle.get("entry") or []) if isinstance(fhir_bundle, dict) else 0
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

    try:
        log.info("Inserting into Supabase (bundle + ekascribe_json)...")
        row = insert_fhir_bundle(
            fhir_bundle,
            ekascribe_json=ekascribe_result,
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
