from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from zapp_atlas.api.deps import get_app_settings
from zapp_atlas.html.templating import templates
from zapp_atlas.settings import AppSettings


router = APIRouter(tags=["html"])


@router.get("/", response_class=HTMLResponse)
def index_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@router.get("/login", response_class=HTMLResponse)
def login_page(
    request: Request,
    settings: Annotated[AppSettings, Depends(get_app_settings)],
) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "login.html", {"dev_auth": settings.dev_auth}
    )


@router.get("/partials/hello", response_class=HTMLResponse)
def hello_partial(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "partials/hello.html")
