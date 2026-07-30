from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from zapp_atlas.api.deps import get_app_settings
from zapp_atlas.auth.deps import CurrentIdentity
from zapp_atlas.html.templating import templates
from zapp_atlas.settings import AppSettings


router = APIRouter(tags=["html"])


@router.get("/", response_class=HTMLResponse)
def index_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@router.get("/login", response_class=HTMLResponse)
def login_page(
    request: Request,
    identity: CurrentIdentity,
    settings: Annotated[AppSettings, Depends(get_app_settings)],
) -> HTMLResponse:
    # Rendered server-side rather than fetched by htmx, so the page arrives in
    # its final state: no empty flash, no extra round trip.
    return templates.TemplateResponse(
        request,
        "login.html",
        {"identity": identity, "dev_auth": settings.dev_auth},
    )


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request) -> HTMLResponse:
    # Placeholder data until the group-scoped endpoints (#130) are wired in;
    # the shapes match those responses so only this import changes later.
    from zapp_atlas.html import dashboard_placeholder as data

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "groups": data.RESEARCH_GROUPS,
            "group": data.CURRENT_GROUP,
            "fish_tank": data.FISH_TANK,
            "cabinet": data.CABINET,
            "submissions": data.SUBMISSIONS,
        },
    )


@router.get("/partials/hello", response_class=HTMLResponse)
def hello_partial(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "partials/hello.html")
