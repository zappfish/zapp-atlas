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

from zapp_atlas.api.routers.cabinet import router as cabinet_router
from zapp_atlas.api.routers.experiments import router as experiments_router
from zapp_atlas.api.routers.exposures import router as exposures_router
from zapp_atlas.api.routers.fish_tank import router as fish_tank_router
from zapp_atlas.api.routers.images import router as images_router
from zapp_atlas.api.routers.observations import router as observations_router
from zapp_atlas.api.routers.research_groups import router as research_groups_router
from zapp_atlas.api.routers.studies import router as studies_router
from zapp_atlas.auth.orcid_public import fetch_public_name
from zapp_atlas.auth.router import router as auth_router
from zapp_atlas.db import get_engine, get_session_factory, init_db
from zapp_atlas.html.edit_router import make_edit_router
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
    # Resolves a bare ORCID to a public display name when admins add group
    # members (#142). On app.state so tests can inject a stub for the network.
    app.state.orcid_name_lookup = fetch_public_name

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
    api.include_router(research_groups_router)
    api.include_router(cabinet_router)
    api.include_router(fish_tank_router)
    app.include_router(api)

    # Static assets for the server-rendered (HTMX) viewing app.
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # The React editing client's compiled JS/CSS. The HTML document that loads
    # them is rendered by the edit router below (templates/edit.html), so that
    # the SPA sits inside the same shell as the server-rendered pages.
    #
    # This mount must be registered *before* the edit router, whose catch-all
    # would otherwise swallow requests for these files.
    client_assets_dir = CLIENT_DIST_DIR / "assets"
    if client_assets_dir.is_dir():
        app.mount(
            "/edit/assets",
            StaticFiles(directory=client_assets_dir),
            name="edit-assets",
        )
    else:
        logger.warning(
            "React client build not found at %s. /edit will explain how to "
            "build it; run `npm run build` in the client/ directory, or set "
            "ZAPP_VITE_DEV_SERVER to use the Vite dev server.",
            CLIENT_DIST_DIR,
        )

    app.include_router(make_edit_router(CLIENT_DIST_DIR))

    return app


# Uvicorn entrypoint: `uvicorn server.api.main:app --reload`
app = create_app()
