"""FastAPI entrypoint for the ZAPP Atlas API.

Notes
-----
* This is intended to replace the legacy Flask server in `server/main.py`.
* For now this module focuses on the "LinkML-first" JSON API (e.g. /studies).
* The LinkML-generated models are imported from the schema package.
"""

from fastapi import FastAPI

from server.api.routers.experiments import router as experiments_router
from server.api.routers.studies import router as studies_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="ZAPP Atlas API",
        version="0.1.0",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(studies_router)
    app.include_router(experiments_router)
    return app


# Uvicorn entrypoint (once wired): `uvicorn server.api.main:app --reload`
app = create_app()
