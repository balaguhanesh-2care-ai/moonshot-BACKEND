from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from services.eka_abdm import create_eka_test_patient, push_fhir_parsing_status, push_fhir_to_eka_records
from services.supabase_client import get_fhir_bundle_by_id

router = APIRouter()


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


class PushFhirBody(BaseModel):
    fhir_bundle: dict
    document_type: str = "ps"
    title: str | None = None
    tags: list[str] | None = None


class DataOnPushBody(BaseModel):
    consent_id: str
    transaction_id: str
    status_response: list[dict]


class PushFhirFromDbBody(BaseModel):
    bundle_id: str
    document_type: str = "ps"
    title: str | None = None
    tags: list[str] | None = None
    include_metadata: bool = True


@router.post("/test-patient")
def create_test_patient(
    full_name: str = "Test Patient",
    dob: str = "1990-01-01",
    gender: str = "M",
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
    Create a test patient in Eka Care. Returns the patient 'oid'.
    EMR auth: X-EkaEmr-Api-Token or (X-EkaEmr-Client-Id + X-EkaEmr-Client-Secret); optional X-EkaEmr-Base-Url. Legacy: X-Eka-*.
    """
    eka_auth = _eka_emr_auth_from_headers(
        x_eka_emr_api_token, x_eka_emr_client_id, x_eka_emr_client_secret, x_eka_emr_base_url,
        x_eka_api_token, x_eka_client_id, x_eka_client_secret, x_eka_base_url,
    )
    try:
        data = create_eka_test_patient(full_name=full_name, dob=dob, gender=gender, eka_auth=eka_auth)
        return {"oid": data.get("oid"), "message": "Use oid as X-Pt-Id header for push-fhir-from-db", **data}
    except Exception as e:
        detail = str(e)
        if hasattr(e, "response") and getattr(e.response, "text", None):
            detail = f"{detail} | EkaCare: {e.response.text[:500]}"
        raise HTTPException(status_code=502, detail=detail)


@router.post("/care-context/data/on-push")
def abdm_data_on_push(
    body: DataOnPushBody,
    x_pt_id: str | None = Header(None, alias="X-Pt-Id"),
    x_partner_pt_id: str | None = Header(None, alias="X-Partner-Pt-Id"),
    x_hip_id: str | None = Header(None, alias="X-Hip-Id"),
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
    Report FHIR parsing status to EkaCare (ABDM HIU data-on-push).
    EMR auth: X-EkaEmr-* or legacy X-Eka-*.
    """
    for item in body.status_response:
        if not isinstance(item.get("care_context_id"), str) or "success" not in item:
            raise HTTPException(
                status_code=400,
                detail="Each status_response item needs care_context_id and success",
            )
    eka_auth = _eka_emr_auth_from_headers(
        x_eka_emr_api_token, x_eka_emr_client_id, x_eka_emr_client_secret, x_eka_emr_base_url,
        x_eka_api_token, x_eka_client_id, x_eka_client_secret, x_eka_base_url,
    )
    try:
        result = push_fhir_parsing_status(
            consent_id=body.consent_id,
            transaction_id=body.transaction_id,
            status_response=body.status_response,
            x_pt_id=x_pt_id,
            x_partner_pt_id=x_partner_pt_id,
            x_hip_id=x_hip_id,
            eka_auth=eka_auth,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/records/push-fhir")
def push_fhir_to_eka(
    body: PushFhirBody,
    x_pt_id: str = Header(..., alias="X-Pt-Id"),
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
    Request EkaCare Records upload with FHIR bundle as metadata.
    EMR auth: X-EkaEmr-* or legacy X-Eka-*.
    """
    if not body.fhir_bundle or body.fhir_bundle.get("resourceType") != "Bundle":
        raise HTTPException(status_code=400, detail="fhir_bundle must be a FHIR Bundle")
    eka_auth = _eka_emr_auth_from_headers(
        x_eka_emr_api_token, x_eka_emr_client_id, x_eka_emr_client_secret, x_eka_emr_base_url,
        x_eka_api_token, x_eka_client_id, x_eka_client_secret, x_eka_base_url,
    )
    try:
        result = push_fhir_to_eka_records(
            fhir_bundle=body.fhir_bundle,
            x_pt_id=x_pt_id,
            document_type=body.document_type,
            title=body.title,
            tags=body.tags,
            eka_auth=eka_auth,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/records/push-fhir-from-db")
def push_fhir_from_supabase_to_eka(
    body: PushFhirFromDbBody,
    x_pt_id: str = Header(..., alias="X-Pt-Id"),
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
    Fetch FHIR bundle from Supabase (fhir_bundles.id) and request EkaCare Records upload.
    EMR auth: X-EkaEmr-* or legacy X-Eka-*.
    """
    bundle = get_fhir_bundle_by_id(body.bundle_id)
    if not bundle or not isinstance(bundle, dict) or bundle.get("resourceType") != "Bundle":
        raise HTTPException(status_code=404, detail="FHIR bundle not found or invalid")
    eka_auth = _eka_emr_auth_from_headers(
        x_eka_emr_api_token, x_eka_emr_client_id, x_eka_emr_client_secret, x_eka_emr_base_url,
        x_eka_api_token, x_eka_client_id, x_eka_client_secret, x_eka_base_url,
    )
    try:
        result = push_fhir_to_eka_records(
            fhir_bundle=bundle,
            x_pt_id=x_pt_id,
            document_type=body.document_type,
            title=body.title,
            tags=body.tags,
            include_metadata=body.include_metadata,
            eka_auth=eka_auth,
        )
        return result
    except Exception as e:
        detail = str(e)
        if hasattr(e, "response") and getattr(e.response, "text", None):
            detail = f"{detail} | EkaCare body: {e.response.text[:500]}"
        raise HTTPException(status_code=502, detail=detail)
