import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import validate_eka_config
from routers import eka_abdm, ekascribe, pipeline, scribe2fhir

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        validate_eka_config()
        log.info("EkaScribe config OK")
    except ValueError:
        log.warning("EkaScribe config missing (optional for pipeline)")
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
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["pipeline"])
app.include_router(eka_abdm.router, prefix="/api/eka-abdm", tags=["eka-abdm"])


@app.get("/health")
def health():
    return {"status": "ok"}
