from fastapi import APIRouter, File, HTTPException, UploadFile

from services.ekascribe import transcribe_audio_files

router = APIRouter()


@router.post("/transcribe")
async def transcribe(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="At least one audio file required")
    try:
        file_tuples = []
        for f in files:
            content = await f.read()
            name = f.filename or "audio"
            file_tuples.append((name, content))
        result = await transcribe_audio_files(file_tuples)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
