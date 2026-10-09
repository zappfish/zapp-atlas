"""The public, server-rendered pages.

The signed-in pages are React and live in client_router.py; their writes go to
/api, which enforces group membership itself (api/authz.py).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from zapp_atlas.api.deps import get_app_settings
from zapp_atlas.auth.deps import CurrentIdentity
from zapp_atlas.html import curation_guidelines
from zapp_atlas.html.templating import templates
from zapp_atlas.settings import AppSettings

router = APIRouter(tags=["html"])


@router.get("/", response_class=HTMLResponse)
def index_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@router.get("/curation-guidelines", response_class=HTMLResponse)
def curation_guidelines_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "curation_guidelines.html",
        {"groups": curation_guidelines.GROUPS},
    )


@router.get("/downloads", response_class=HTMLResponse)
def downloads_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "coming_soon.html", {"heading": "Downloads"})


@router.get("/help", response_class=HTMLResponse)
def help_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "coming_soon.html", {"heading": "Help"})


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


@router.get("/partials/hello", response_class=HTMLResponse)
def hello_partial(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "partials/hello.html")
