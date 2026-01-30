from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from agent import run_mapping_agent
from services.supabase_client import get_first_fhir_bundle

router = APIRouter()


def _groq_from_app(request: Request) -> tuple[str | None, str | None]:
    state = getattr(request.app, "state", None)
    if state is None:
        return None, None
    return getattr(state, "groq_api_key", None), getattr(state, "groq_model", None)


class MappingAgentInput(BaseModel):
    api_doc_url: str = Field(default="", description="EMR API documentation URL (used to generate search queries)")
    emr_id: str = Field(default="default", description="Identifier for this EMR; mapping stored under this id")


@router.post("/mapping")
def run_mapping(request: Request, body: MappingAgentInput | dict[str, Any] | None = None):
    """
    Run the EMR mapping agent: searches the web for EMR API docs, reads them,
    produces a mapping from FHIR (sample bundle from DB) to the EMR structure,
    and stores push_fhir / get_fhir mapping in Supabase. No API trial.
    Sample bundle: first row from fhir_bundles (bundle_json), by created_at.
    """
    data = (body.model_dump(exclude_none=True) if isinstance(body, MappingAgentInput) else body) if body else {}
    bundle = get_first_fhir_bundle()
    if bundle is None:
        raise HTTPException(status_code=400, detail="No FHIR bundle in DB (fhir_bundles table empty)")
    data["fhir_bundle"] = bundle
    groq_api_key, groq_model = _groq_from_app(request)
    try:
        result = run_mapping_agent(data, groq_api_key=groq_api_key, groq_model=groq_model)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
