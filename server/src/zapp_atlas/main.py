"""FastAPI entrypoint for the ZAPP Atlas API.

Notes
-----
* Replaces the legacy Flask server archived under ``legacy/server/main.py``.
* The LinkML-generated models are imported from the schema package.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles

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


logger = logging.getLogger(__name__)

PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "html" / "static"
# Built React editing client. Lives at the repo-root `client/` (sibling of
# `server/`); served at `/edit` once it has been built (`npm run build`).
CLIENT_DIST_DIR = PACKAGE_DIR.parents[2] / "client" / "dist"


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

    # Static assets for the server-rendered (HTMX) viewing app.
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # The React editing client, served under /edit in production. In
    # development it is run from the Vite dev server instead. Mount only when a
    # build exists so the server still boots before the client is built.
    if CLIENT_DIST_DIR.is_dir():
        app.mount("/edit", StaticFiles(directory=CLIENT_DIST_DIR, html=True), name="edit")
    else:
        logger.warning(
            "React client build not found at %s; /edit will not be served. "
            "Run `npm run build` in the client/ directory.",
            CLIENT_DIST_DIR,
        )

    return app


# Uvicorn entrypoint: `uvicorn server.api.main:app --reload`
app = create_app()
