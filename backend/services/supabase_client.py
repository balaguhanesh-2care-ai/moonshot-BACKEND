import logging
from typing import Any

from config import SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL

log = logging.getLogger(__name__)


def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or NEXT_PUBLIC_* equivalents) are required")
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def insert_fhir_bundle(
    bundle_json: dict[str, Any],
    *,
    ekascribe_json: dict[str, Any] | None = None,
    patient_id: str | None = None,
    encounter_id: str | None = None,
    txn_id: str | None = None,
) -> dict[str, Any]:
    client = get_supabase_client()
    row = {
        "bundle_json": bundle_json,
        "ekascribe_json": ekascribe_json,
        "patient_id": patient_id,
        "encounter_id": encounter_id,
        "txn_id": txn_id,
    }
    result = client.table("fhir_bundles").insert(row).execute()
    if not result.data or len(result.data) == 0:
        raise RuntimeError("Supabase insert returned no data")
    inserted = result.data[0]
    log.info("Supabase insert fhir_bundles id=%s", inserted.get("id"))
    return inserted
