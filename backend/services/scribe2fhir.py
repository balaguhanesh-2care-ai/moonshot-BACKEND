try:
    import scribe2fhir as s2f
except ImportError:
    s2f = None


def is_available() -> bool:
    return s2f is not None


async def submit_document(file_content: bytes, filename: str) -> dict:
    if not is_available():
        raise RuntimeError(
            "scribe2fhir package is not installed or not importable. "
            "Install with: pip install scribe2fhir"
        )
    raise NotImplementedError(
        "scribe2fhir SDK integration: implement once package API is confirmed"
    )
