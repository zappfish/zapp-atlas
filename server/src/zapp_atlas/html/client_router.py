"""The host routes for the React client.

Serves the shell document React mounts into. The routes here and the ones in
html/router.py share a single URL space — Jinja renders the public pages,
React the dashboard and the submission form — so this file names the paths it
owns rather than claiming a subtree.

Registered *after* the /assets mount in create_app, so that neither the
catch-all below nor any route added later shadows the built asset files.
"""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse

from zapp_atlas.api.deps import get_app_settings
from zapp_atlas.html.templating import templates
from zapp_atlas.html.vite import ViteAssetsUnavailable, get_vite_assets
from zapp_atlas.settings import AppSettings


def make_client_router(dist_dir: Path) -> APIRouter:
    router = APIRouter(tags=["html"])

    # A catch-all so client-side routes (/edit/studies/1, …) deep-link to the
    # same document; React reads the path and renders the right view.
    @router.get("/edit", response_class=HTMLResponse)
    @router.get("/edit/{client_path:path}", response_class=HTMLResponse)
    def edit_page(
        request: Request,
        settings: Annotated[AppSettings, Depends(get_app_settings)],
        client_path: str = "",
    ) -> HTMLResponse:
        try:
            vite = get_vite_assets(dist_dir, settings.vite_dev_server)
        except ViteAssetsUnavailable as exc:
            return templates.TemplateResponse(
                request,
                "edit_unavailable.html",
                {"message": str(exc)},
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return templates.TemplateResponse(request, "edit.html", {"vite": vite})

    return router
