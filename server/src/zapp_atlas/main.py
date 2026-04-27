"""FastAPI entrypoint for the ZAPP Atlas API.

Notes
-----
* Replaces the legacy Flask server archived under ``legacy/server/main.py``.
* The LinkML-generated models are imported from the schema package.
"""

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from zapp_atlas.auth.router import router as auth_router
from zapp_atlas.api.routers.experiments import router as experiments_router
from zapp_atlas.api.routers.exposures import router as exposures_router
from zapp_atlas.api.routers.images import router as images_router
from zapp_atlas.api.routers.observations import router as observations_router
from zapp_atlas.api.routers.studies import router as studies_router
from zapp_atlas.db import get_engine, get_session_factory, init_db
from zapp_atlas.html.router import router as html_router
from zapp_atlas.seed import seed
from zapp_atlas.settings import AppSettings, load_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = app.state.settings
    engine = get_engine(settings=settings)
    app.state.engine = engine
    app.state.session_factory = get_session_factory(engine)
    init_db(engine)
    if not settings.skip_seed:
        Session = app.state.session_factory
        with Session() as session:
            seed(session)
    yield


def create_app(settings: AppSettings | None = None) -> FastAPI:
    app = FastAPI(
        title="ZAPP Atlas API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.settings = settings or load_settings()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(html_router)
    app.include_router(auth_router)

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
