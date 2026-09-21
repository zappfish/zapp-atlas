"""The host routes for the React client.

Serves the shell document React mounts into. The routes here and the ones in
html/router.py share a single URL space — Jinja renders the public pages,
React the dashboard and the submission form — so this file names the paths it
owns rather than claiming a subtree.

Every route here returns the same empty shell; the path only tells React which
view to render once it has booted. Routes that need a signed-in caller check
for one before rendering, so a deep link from a signed-out browser lands on
/login rather than on a frame that empties itself a moment later.

Registered *after* the /assets mount in create_app, so that neither the
catch-all below nor any route added later shadows the built asset files.
"""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from zapp_atlas.api.deps import get_app_settings
from zapp_atlas.auth.deps import CurrentIdentity
from zapp_atlas.html.templating import templates
from zapp_atlas.html.vite import ViteAssetsUnavailable, get_vite_assets
from zapp_atlas.settings import AppSettings


def make_client_router(dist_dir: Path) -> APIRouter:
    router = APIRouter(tags=["html"])

    def shell(request: Request, settings: AppSettings) -> HTMLResponse:
        """The document React mounts into: the site shell around an empty div.

        It carries no page data. Whatever the client renders it fetches from
        /api once it has booted, so this is the same response for every route.
        """
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

    @router.get("/dashboard", response_class=HTMLResponse)
    def dashboard_page(
        request: Request,
        identity: CurrentIdentity,
        settings: Annotated[AppSettings, Depends(get_app_settings)],
    ) -> Response:
        # Gated here rather than in React: a signed-out visitor is sent to
        # /login before any HTML goes out, instead of loading the page,
        # booting React, and only then being bounced.
        #
        # Being signed in is all this checks. Whether the caller may see a
        # particular group's records is the API's call — see api/authz.py.
        if identity is None:
            return RedirectResponse("/login", status_code=303)
        return shell(request, settings)

    # The editing form's old home. Superseded by the routes above as pages
    # move to React; kept until nothing links here.
    @router.get("/edit", response_class=HTMLResponse)
    @router.get("/edit/{client_path:path}", response_class=HTMLResponse)
    def edit_page(
        request: Request,
        settings: Annotated[AppSettings, Depends(get_app_settings)],
        client_path: str = "",
    ) -> HTMLResponse:
        return shell(request, settings)

    return router
