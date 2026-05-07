"""FastAPI entrypoint for the ZAPP Atlas API.

Notes
-----
* Replaces the legacy Flask server archived under ``legacy/server/main.py``.
* The LinkML-generated models are imported from the schema package.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from zapp_atlas.api.routers.chemicals import router as chemicals_router
from zapp_atlas.api.routers.experiments import router as experiments_router
from zapp_atlas.api.routers.exposures import router as exposures_router
from zapp_atlas.api.routers.images import router as images_router
from zapp_atlas.api.routers.observations import router as observations_router
from zapp_atlas.api.routers.studies import router as studies_router
from zapp_atlas.api.routers.submission import router as submission_router
from zapp_atlas.db import get_engine, get_session_factory, init_db
from zapp_atlas.seed import seed

# client/dist relative to repo root (5 levels up from this file)
_REPO_ROOT = Path(__file__).resolve().parents[3]
_DIST_DIR = _REPO_ROOT / "client" / "dist"


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

    # Atlas data API
    api = APIRouter(prefix="/api")
    api.include_router(studies_router)
    api.include_router(experiments_router)
    api.include_router(exposures_router)
    api.include_router(observations_router)
    api.include_router(images_router)
    app.include_router(api)

    # Chemical normalization routes (already prefixed /api/chemicals)
    app.include_router(chemicals_router)

    # Annotation form submission
    app.include_router(submission_router)

    # Static files + SPA fallback (must come last)
    if _DIST_DIR.exists():
        app.mount("/assets", StaticFiles(directory=str(_DIST_DIR / "assets")), name="assets")

    @app.get("/", include_in_schema=False)
    def serve_index() -> FileResponse:
        index = _DIST_DIR / "index.html"
        if index.is_file():
            return FileResponse(str(index))
        raise HTTPException(status_code=404, detail="Client not built — run 'npm run build' in client/")

    @app.get("/{path:path}", include_in_schema=False)
    def serve_spa(path: str) -> FileResponse:
        if not _DIST_DIR.exists():
            raise HTTPException(status_code=404, detail="Client not built")
        file_path = (_DIST_DIR / path).resolve()
        try:
            file_path.relative_to(_DIST_DIR)
        except ValueError:
            raise HTTPException(status_code=404)
        if file_path.is_file():
            return FileResponse(str(file_path))
        # SPA fallback for route-like paths (no extension in last segment)
        if "." not in path.rsplit("/", 1)[-1]:
            index = _DIST_DIR / "index.html"
            if index.is_file():
                return FileResponse(str(index))
        raise HTTPException(status_code=404)

    return app


# Uvicorn entrypoint: uvicorn zapp_atlas.main:app --reload
app = create_app()
