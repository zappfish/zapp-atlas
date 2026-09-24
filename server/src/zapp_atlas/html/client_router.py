"""The host routes for the React client.

Every route here returns the same empty shell; the path only tells React which
view to render once it has booted. They share a URL space with html/router.py,
which renders the public pages, so this file lists the paths it owns rather
than claiming a subtree.

Keep this list and the client's routes in App.tsx in agreement: a path served
here but unknown to React renders an empty page, and one React knows but this
does not 404s on a direct load.

Registered after the /assets mount in create_app, so no route here shadows the
built asset files.
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
                "app_unavailable.html",
                {"message": str(exc)},
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return templates.TemplateResponse(request, "app.html", {"vite": vite})

    # Gated here rather than in React: a signed-out visitor is sent to /login
    # before any HTML goes out, instead of loading the page, booting React,
    # and only then being bounced.
    #
    # Being signed in is all this checks. Whether the caller may see a
    # particular group's records is the API's call — see api/authz.py.
    @router.get("/my-submissions", response_class=HTMLResponse)
    def my_submissions_page(
        request: Request,
        identity: CurrentIdentity,
        settings: Annotated[AppSettings, Depends(get_app_settings)],
    ) -> Response:
        if identity is None:
            return RedirectResponse("/login", status_code=303)
        return shell(request, settings)

    @router.get("/submissions/new", response_class=HTMLResponse)
    def new_submission_page(
        request: Request,
        identity: CurrentIdentity,
        settings: Annotated[AppSettings, Depends(get_app_settings)],
    ) -> Response:
        if identity is None:
            return RedirectResponse("/login", status_code=303)
        return shell(request, settings)

    @router.get("/research-groups/{group_id}", response_class=HTMLResponse)
    def research_group_page(
        request: Request,
        identity: CurrentIdentity,
        settings: Annotated[AppSettings, Depends(get_app_settings)],
        group_id: int,
    ) -> Response:
        if identity is None:
            return RedirectResponse("/login", status_code=303)
        return shell(request, settings)

    @router.get(
        "/research-groups/{group_id}/fish-tank/{entry_id}",
        response_class=HTMLResponse,
    )
    @router.get(
        "/research-groups/{group_id}/chemical-cabinet/{entry_id}",
        response_class=HTMLResponse,
    )
    def record_detail_page(
        request: Request,
        identity: CurrentIdentity,
        settings: Annotated[AppSettings, Depends(get_app_settings)],
        group_id: int,
        entry_id: int,
    ) -> Response:
        if identity is None:
            return RedirectResponse("/login", status_code=303)
        return shell(request, settings)

    return router
