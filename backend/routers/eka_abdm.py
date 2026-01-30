from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from services.eka_abdm import create_eka_test_patient, push_fhir_parsing_status, push_fhir_to_eka_records
from services.supabase_client import get_fhir_bundle_by_id

router = APIRouter()


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
):
    """
    Create a test patient in Eka Care. Returns the patient 'oid'.
    Use that oid as X-Pt-Id when calling push-fhir-from-db.
    """
    try:
        data = create_eka_test_patient(full_name=full_name, dob=dob, gender=gender)
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
):
    """
    Report FHIR parsing status to EkaCare (ABDM HIU data-on-push).

    Call after you receive care context data from EkaCare. status_response items
    must have: care_context_id (str), success (bool), description (str).
    """
    for item in body.status_response:
        if not isinstance(item.get("care_context_id"), str) or "success" not in item:
            raise HTTPException(
                status_code=400,
                detail="Each status_response item needs care_context_id and success",
            )
    try:
        result = push_fhir_parsing_status(
            consent_id=body.consent_id,
            transaction_id=body.transaction_id,
            status_response=body.status_response,
            x_pt_id=x_pt_id,
            x_partner_pt_id=x_partner_pt_id,
            x_hip_id=x_hip_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/records/push-fhir")
def push_fhir_to_eka(
    body: PushFhirBody,
    x_pt_id: str = Header(..., alias="X-Pt-Id"),
):
    """
    Request EkaCare Records upload with FHIR bundle as metadata.

    Body: fhir_bundle (FHIR Bundle), optional document_type, title, tags.
    Header X-Pt-Id = Eka user id (OID). Returns presigned upload response.
    """
    if not body.fhir_bundle or body.fhir_bundle.get("resourceType") != "Bundle":
        raise HTTPException(status_code=400, detail="fhir_bundle must be a FHIR Bundle")
    try:
        result = push_fhir_to_eka_records(
            fhir_bundle=body.fhir_bundle,
            x_pt_id=x_pt_id,
            document_type=body.document_type,
            title=body.title,
            tags=body.tags,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/records/push-fhir-from-db")
def push_fhir_from_supabase_to_eka(
    body: PushFhirFromDbBody,
    x_pt_id: str = Header(..., alias="X-Pt-Id"),
):
    """
    Fetch FHIR bundle from Supabase (fhir_bundles.id) and request EkaCare Records
    upload. Header X-Pt-Id = Eka user id (OID). Set include_metadata=false to
    test upload without FHIR metadata (isolate 500).
    """
    bundle = get_fhir_bundle_by_id(body.bundle_id)
    if not bundle or not isinstance(bundle, dict) or bundle.get("resourceType") != "Bundle":
        raise HTTPException(status_code=404, detail="FHIR bundle not found or invalid")
    try:
        result = push_fhir_to_eka_records(
            fhir_bundle=bundle,
            x_pt_id=x_pt_id,
            document_type=body.document_type,
            title=body.title,
            tags=body.tags,
            include_metadata=body.include_metadata,
        )
        return result
    except Exception as e:
        detail = str(e)
        if hasattr(e, "response") and getattr(e.response, "text", None):
            detail = f"{detail} | EkaCare body: {e.response.text[:500]}"
        raise HTTPException(status_code=502, detail=detail)
