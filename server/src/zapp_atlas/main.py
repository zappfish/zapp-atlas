"""FastAPI entrypoint for the ZAPP Atlas API.

Notes
-----
* Replaces the legacy Flask server archived under ``legacy/server/main.py``.
* The LinkML-generated models are imported from the schema package.
"""

import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from zapp_atlas.api.routers.experiments import router as experiments_router
from zapp_atlas.api.routers.exposures import router as exposures_router
from zapp_atlas.api.routers.images import router as images_router
from zapp_atlas.api.routers.observations import router as observations_router
from zapp_atlas.api.routers.studies import router as studies_router
from zapp_atlas.db import get_engine, get_session_factory, init_db
from zapp_atlas.seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    init_db(engine)
    if os.getenv("ZAPP_SKIP_SEED", "").lower() not in {"1", "true", "yes"}:
        Session = get_session_factory(engine)
        with Session() as session:
            seed(session)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="ZAPP Atlas API",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    api = APIRouter(prefix="/api")
    api.include_router(studies_router)
    api.include_router(experiments_router)
    api.include_router(exposures_router)
    api.include_router(observations_router)
    api.include_router(images_router)
    app.include_router(api)

    return app


# Uvicorn entrypoint: `uvicorn server.api.main:app --reload`
app = create_app()
