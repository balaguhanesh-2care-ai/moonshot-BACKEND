from fastapi import APIRouter, File, HTTPException, UploadFile

from services.scribe2fhir import is_available, submit_document

router = APIRouter()


@router.get("/health")
def scribe2fhir_health():
    return {"available": is_available()}


@router.post("/submit")
async def submit(file: UploadFile = File(...)):
    if not is_available():
        raise HTTPException(
            status_code=503,
            detail="scribe2fhir SDK not installed or not importable",
        )
    try:
        content = await file.read()
        name = file.filename or "document"
        return await submit_document(content, name)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
