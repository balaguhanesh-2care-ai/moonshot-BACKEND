import logging

try:
    import scribe2fhir as s2f
except ImportError:
    s2f = None

log = logging.getLogger(__name__)


def is_available() -> bool:
    return s2f is not None


def emr_json_to_fhir_bundle(ekascribe_result: dict) -> dict:
    if not is_available():
        raise RuntimeError(
            "scribe2fhir package is not installed or not importable. "
            "Install with: pip install scribe2fhir"
        )
    from services.ekascribe_to_fhir import ekascribe_result_to_fhir_bundle
    bundle = ekascribe_result_to_fhir_bundle(ekascribe_result)
    entry_count = len(bundle.get("entry") or []) if isinstance(bundle, dict) else 0
    log.info("scribe2fhir: built FHIR bundle with %d entries", entry_count)
    return bundle


async def submit_document(file_content: bytes, filename: str) -> dict:
    if not is_available():
        raise RuntimeError(
            "scribe2fhir package is not installed or not importable. "
            "Install with: pip install scribe2fhir"
        )
    raise NotImplementedError(
        "scribe2fhir SDK integration: implement once package API is confirmed"
    )
