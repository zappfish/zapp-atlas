"""FastAPI entrypoint for the ZAPP Atlas API.

Notes
-----
* Replaces the legacy Flask server archived under ``legacy/server/main.py``.
* The LinkML-generated models are imported from the schema package.
"""

import os
from contextlib import asynccontextmanager

import fastapi._compat.v2 as _fastapi_compat_v2
from fastapi import APIRouter, FastAPI

from server.api.routers.experiments import router as experiments_router
from server.api.routers.exposures import router as exposures_router
from server.api.routers.images import router as images_router
from server.api.routers.observations import router as observations_router
from server.api.routers.studies import router as studies_router
from server.db import get_engine, get_session_factory, init_db
from server.seed import seed


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
