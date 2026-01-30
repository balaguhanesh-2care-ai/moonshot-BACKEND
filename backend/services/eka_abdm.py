import io
import json
import logging
import time
from typing import Any

import httpx
import requests

from config import EKAEMR_BASE_URL, get_eka_emr_headers, get_eka_emr_headers_from_params

log = logging.getLogger(__name__)

EKAEMR_BASE = "https://api.eka.care"
ABDM_DATA_ON_PUSH_URL = f"{EKAEMR_BASE}/abdm/v1/hiu/care-context/data/on-push"
RECORDS_OBTAIN_AUTH_URL = f"{EKAEMR_BASE}/mr/api/v1/docs"
PATIENT_CREATE_URL = f"{EKAEMR_BASE}/profiles/v1/patient/"


def _minimal_pdf_bytes(title: str = "Scribe to EkaCare") -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, title)
    c.drawString(100, 730, "Generated from Scribe pipeline. FHIR metadata attached.")
    c.save()
    return buf.getvalue()


def _eka_headers_and_base(eka_auth: dict[str, Any] | None) -> tuple[dict[str, str], str]:
    if eka_auth and (eka_auth.get("api_token") or (eka_auth.get("client_id") and eka_auth.get("client_secret"))):
        return get_eka_emr_headers_from_params(
            api_token=eka_auth.get("api_token"),
            client_id=eka_auth.get("client_id"),
            client_secret=eka_auth.get("client_secret"),
            base_url=eka_auth.get("base_url"),
        )
    return get_eka_emr_headers(), (EKAEMR_BASE_URL or EKAEMR_BASE).rstrip("/")


def push_fhir_parsing_status(
    consent_id: str,
    transaction_id: str,
    status_response: list[dict[str, Any]],
    *,
    x_pt_id: str | None = None,
    x_partner_pt_id: str | None = None,
    x_hip_id: str | None = None,
    base_url: str = EKAEMR_BASE,
    eka_auth: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Report care context FHIR parsing status to EkaCare (HIU data-on-push).

    Call this after you receive and parse care context data from EkaCare (HIP).
    Each item in status_response should have: care_context_id, success (bool), description (str).
    """
    headers, base = _eka_headers_and_base(eka_auth)
    url = f"{base.rstrip('/')}/abdm/v1/hiu/care-context/data/on-push"
    body = {
        "consent_id": consent_id,
        "transaction_id": transaction_id,
        "status_response": status_response,
    }
    headers = {**headers, "Content-Type": "application/json"}
    if x_pt_id:
        headers["X-Pt-Id"] = x_pt_id
    if x_partner_pt_id:
        headers["X-Partner-Pt-Id"] = x_partner_pt_id
    if x_hip_id:
        headers["X-Hip-Id"] = x_hip_id

    with httpx.Client() as client:
        r = client.post(url, json=body, headers=headers, timeout=30.0)
    if r.status_code not in (200, 202):
        log.error("EkaCare data-on-push %s: %s", r.status_code, r.text[:500])
        r.raise_for_status()
    return r.json() if r.content else {}


def _metadata_for_eka(fhir_bundle: dict[str, Any], max_chars: int = 15000) -> dict[str, Any]:
    """Reduce bundle size for EkaCare metadata to avoid 500 (server limit)."""
    raw = json.dumps(fhir_bundle, separators=(",", ":"))
    if len(raw) <= max_chars:
        return fhir_bundle
    entries = fhir_bundle.get("entry") or []
    summary = [
        {"resource": {"resourceType": e.get("resource", {}).get("resourceType"), "id": e.get("resource", {}).get("id")}}
        for e in entries[:20]
    ]
    return {
        "resourceType": fhir_bundle.get("resourceType", "Bundle"),
        "type": fhir_bundle.get("type", "collection"),
        "total": len(entries),
        "entry": summary,
    }


def push_fhir_to_eka_records(
    fhir_bundle: dict[str, Any],
    *,
    x_pt_id: str,
    document_type: str = "ps",
    title: str | None = None,
    tags: list[str] | None = None,
    base_url: str | None = None,
    include_metadata: bool = True,
    eka_auth: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Full two-step EkaCare Records upload: Step 1 obtain presigned URL (with FHIR
    bundle as metadata), Step 2 upload a minimal PDF to that URL. Returns
    document_id and batch_response. Requires real file (PDF) per API spec.
    Set include_metadata=False to test without FHIR metadata (isolate 500).
    """
    eka_headers, base = _eka_headers_and_base(eka_auth)
    base_url = (base_url or base).rstrip("/")
    pdf_bytes = _minimal_pdf_bytes(title=title or "Scribe to EkaCare")
    file_size = len(pdf_bytes)

    url = f"{base_url}/mr/api/v1/docs"
    headers = {**eka_headers, "Content-Type": "application/json", "X-Pt-Id": x_pt_id}
    batch_request = {
        "dt": document_type,
        "dd_e": int(time.time()),
        "files": [{"contentType": "application/pdf", "file_size": file_size}],
    }
    if include_metadata:
        metadata_payload = _metadata_for_eka(fhir_bundle)
        batch_request["metadata"] = json.dumps(metadata_payload)
    if title:
        batch_request["title"] = title[:256]
    if tags:
        batch_request["tg"] = tags[:10]

    with httpx.Client() as client:
        r = client.post(url, json={"batch_request": [batch_request]}, headers=headers, timeout=30.0)
    if r.status_code != 200:
        err_body = (r.text or "").strip()[:1000] or "(empty body)"
        log.error("EkaCare records obtain-auth %s: %s", r.status_code, err_body)
        r.raise_for_status()

    data = r.json()
    batch_response = data.get("batch_response") or []
    if not batch_response:
        log.warning("EkaCare records: batch_response empty")
        return data

    first = batch_response[0]
    if first.get("error_details"):
        err = first["error_details"]
        log.error("EkaCare batch error: %s", err)
        raise RuntimeError(f"EkaCare batch error: {err}")

    forms = first.get("forms") or []
    document_id = first.get("document_id")
    for form in forms:
        upload_url = form.get("url")
        upload_fields = form.get("fields") or {}
        if not upload_url:
            continue
        form_data = list(upload_fields.items())
        files = {"file": ("document.pdf", pdf_bytes, "application/pdf")}
        try:
            resp = requests.post(
                upload_url,
                data=form_data,
                files=files,
                timeout=60,
            )
        except Exception as e:
            log.exception("EkaCare Step 2 upload failed: %s", e)
            raise
        if resp.status_code not in (200, 204):
            log.error("EkaCare Step 2 upload %s: %s", resp.status_code, resp.text[:500])
            resp.raise_for_status()
        log.info("EkaCare record uploaded document_id=%s", document_id)
        break

    return {"document_id": document_id, "batch_response": batch_response, **data}


def create_eka_test_patient(
    *,
    full_name: str = "Test Patient",
    dob: str = "1990-01-01",
    gender: str = "M",
    client_id: str | None = None,
    base_url: str | None = None,
    eka_auth: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create a test patient in Eka Care. Returns the created patient with 'oid'.
    Use that oid as X-Pt-Id for Records API. Requires Eka auth (api_token or client_id+client_secret).
    """
    from config import EKAEMR_CLIENT_ID

    eka_headers, base = _eka_headers_and_base(eka_auth)
    base_url = (base_url or base).rstrip("/")
    url = f"{base_url}/profiles/v1/patient/"
    eka_client_id = (eka_auth or {}).get("client_id") or EKAEMR_CLIENT_ID or "doc"
    headers = {
        **eka_headers,
        "Content-Type": "application/json",
        "client-id": client_id or eka_client_id,
    }
    body = {"fln": full_name[:256], "dob": dob, "gen": gender}
    with httpx.Client() as client:
        r = client.post(url, json=body, headers=headers, timeout=30.0)
    if r.status_code not in (200, 201):
        log.error("EkaCare create patient %s: %s", r.status_code, r.text[:500])
        r.raise_for_status()
    data = r.json() if r.content else {}
    log.info("EkaCare patient created oid=%s", data.get("oid"))
    return data
