"""FastAPI entrypoint for the ZAPP Atlas API.

Notes
-----
* This is intended to replace the legacy Flask server in `server/main.py`.
* For now this module focuses on the "LinkML-first" JSON API (e.g. /studies).
* The LinkML-generated models are imported from the schema package.
"""

from contextlib import asynccontextmanager
from pathlib import Path

import fastapi._compat.v2 as _fastapi_compat_v2
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from server.api.routers.experiments import router as experiments_router
from server.api.routers.studies import router as studies_router
from server.db import init_db


# ---------------------------------------------------------------------------
# Patch FastAPI's JSON-schema generator for LinkML-generated "enum" classes.
#
# LinkML sometimes emits bare ``str`` subclasses (e.g. ExposureRouteEnum)
# instead of proper ``enum.Enum`` types.  Pydantic validates them with
# ``core_schema.is_instance_schema()``, which has no JSON Schema mapping and
# raises ``PydanticInvalidForJsonSchema``.
#
# We subclass FastAPI's own ``GenerateJsonSchema`` (in ``fastapi._compat.v2``)
# so that any str subclass is emitted as ``{"type": "string"}``, then replace
# the module-level reference that ``get_definitions`` uses.
# ---------------------------------------------------------------------------
class _LenientJsonSchema(_fastapi_compat_v2.GenerateJsonSchema):
    def is_instance_schema(self, schema: dict) -> dict:  # type: ignore[override]
        cls = schema.get("cls")
        if cls is not None and issubclass(cls, str):
            return {"type": "string"}
        return super().is_instance_schema(schema)


_fastapi_compat_v2.GenerateJsonSchema = _LenientJsonSchema  # type: ignore[misc]

DIST_DIR = Path(__file__).resolve().parent.parent.parent / "client" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
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

    app.include_router(studies_router)
    app.include_router(experiments_router)

    # Serve Vite's hashed asset bundles (JS/CSS) if the build exists
    assets_dir = DIST_DIR / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # SPA catch-all: serve files from dist/ if they exist, otherwise index.html
    if DIST_DIR.is_dir():

        @app.get("/{full_path:path}")
        async def spa_catch_all(full_path: str):
            file = DIST_DIR / full_path
            if full_path and file.is_file():
                return FileResponse(file)
            return FileResponse(DIST_DIR / "index.html")

    return app


# Uvicorn entrypoint (once wired): `uvicorn server.api.main:app --reload`
app = create_app()
