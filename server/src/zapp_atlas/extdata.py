"""Serve the client-facing files of the extdata ontology bundle.

The bundle is built by ``extdata/`` at the repo root (see its README) and
named by a hash of its inputs. Files are served at
``/extdata/<hash>/<name>``, so the content at a URL never changes and browsers
may cache it indefinitely. ``/extdata/manifest.json`` is the one unversioned
URL: it is how a client learns the current hash, so it is never cached.

The JSON files are large (tens of MB) and the bundle ships them gzipped too.
The gzipped copy is sent as-is to any client that accepts it, rather than
compressing on every request.

Only the files a browser needs are exposed; labels.db is for the server's own
use.
"""

import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

PUBLIC_FILES = {
    "zp.json": "application/json",
    "zfa.json": "application/json",
    "zfin_counts.tsv": "text/tab-separated-values; charset=utf-8",
}

IMMUTABLE = "public, max-age=31536000, immutable"


def load_manifest(dist_dir: Path) -> dict | None:
    path = dist_dir / "manifest.json"
    if not path.is_file():
        logger.warning(
            "extdata bundle not found at %s; /extdata will answer 404. "
            "Build it with `just extdata`.",
            dist_dir,
        )
        return None
    return json.loads(path.read_text())


def accepts_gzip(request: Request) -> bool:
    for coding in request.headers.get("accept-encoding", "").split(","):
        name, _, params = coding.strip().partition(";")
        if name.strip().lower() == "gzip" and params.replace(" ", "") != "q=0":
            return True
    return False


def make_extdata_router(dist_dir: Path) -> APIRouter:
    manifest = load_manifest(dist_dir)
    router = APIRouter(prefix="/extdata", tags=["extdata"])

    def not_found() -> HTTPException:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    @router.get("/manifest.json")
    def manifest_file() -> FileResponse:
        if manifest is None:
            raise not_found()
        return FileResponse(
            dist_dir / "manifest.json",
            media_type="application/json",
            headers={"Cache-Control": "no-cache"},
        )

    @router.get("/{bundle_hash}/{name}")
    def bundle_file(bundle_hash: str, name: str, request: Request) -> FileResponse:
        # A request for an older hash is a 404 rather than the current file:
        # serving different content at a URL marked immutable would leave
        # browsers caching the wrong data for good.
        if manifest is None or bundle_hash != manifest["hash"] or name not in PUBLIC_FILES:
            raise not_found()

        headers = {"Cache-Control": IMMUTABLE, "Vary": "Accept-Encoding"}
        gzipped = f"{name}.gz"
        if gzipped in manifest["files"] and accepts_gzip(request):
            return FileResponse(
                dist_dir / gzipped,
                media_type=PUBLIC_FILES[name],
                headers={**headers, "Content-Encoding": "gzip"},
            )
        return FileResponse(dist_dir / name, media_type=PUBLIC_FILES[name], headers=headers)

    return router
