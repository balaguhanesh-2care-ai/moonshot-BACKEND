from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import validate_eka_config
from routers import ekascribe, scribe2fhir


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        validate_eka_config()
    except ValueError:
        pass
    yield


app = FastAPI(
    title="Moonshot Backend",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ekascribe.router, prefix="/api/ekascribe", tags=["ekascribe"])
app.include_router(scribe2fhir.router, prefix="/api/scribe2fhir", tags=["scribe2fhir"])


@app.get("/health")
def health():
    return {"status": "ok"}
