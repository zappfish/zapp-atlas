import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from db import init_db
from routers import router

SERVER_DIR = Path(__file__).resolve().parent
REPO_ROOT = SERVER_DIR.parent
DIST_DIR = (REPO_ROOT / "client" / "dist").resolve()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}


# Static file serving with SPA fallback
if DIST_DIR.exists() and (DIST_DIR / "index.html").exists():
    @app.get("/")
    def serve_index():
        return FileResponse(DIST_DIR / "index.html")

    # Mount static assets directory so JS/CSS/images are served directly
    app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

    @app.get("/{path:path}")
    def serve_dist(path: str):
        file_path = (DIST_DIR / path).resolve()
        # Prevent directory traversal
        try:
            file_path.relative_to(DIST_DIR)
        except ValueError:
            return JSONResponse({"detail": "Not found"}, status_code=404)

        if file_path.is_file():
            return FileResponse(file_path)

        # SPA fallback: route-like paths (no dot in last segment) get index.html
        last_segment = path.rsplit("/", 1)[-1]
        if "." not in last_segment:
            return FileResponse(DIST_DIR / "index.html")

        return JSONResponse({"detail": "Not found"}, status_code=404)


def main():
    import uvicorn
    port = int(os.getenv("PORT", "5000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    main()
