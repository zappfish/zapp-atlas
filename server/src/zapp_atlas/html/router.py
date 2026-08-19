from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from zapp_atlas.api.deps import get_app_settings, get_session
from zapp_atlas.auth.deps import CurrentIdentity
from zapp_atlas.html.templating import templates
from zapp_atlas.settings import AppSettings


router = APIRouter(tags=["html"])


def _redirect(request: Request, target: str) -> Response:
    # htmx follows a 3xx into its swap target; HX-Redirect navigates the whole
    # page instead. A direct load gets a plain redirect.
    if request.headers.get("HX-Request"):
        return Response(status_code=204, headers={"HX-Redirect": target})
    return RedirectResponse(target, status_code=303)


def _login_redirect(request: Request) -> Response:
    return _redirect(request, "/login")


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


def _dash_template(request: Request, full: str, body: str) -> str:
    # Sidebar navigation is an htmx request: return just the swapped #dash-body.
    # A direct load returns the full page.
    return body if request.headers.get("HX-Request") else full


@router.get("/my-submissions", response_class=HTMLResponse)
def my_submissions_page(
    request: Request, identity: CurrentIdentity, view: str = "list"
) -> Response:
    # Post-login landing. The sidebar renders the group list and total count.
    # `view` toggles the submissions between the list and a card grid.
    if identity is None:
        return _login_redirect(request)

    from zapp_atlas.html import dashboard_placeholder as data

    template = _dash_template(
        request, "my_submissions.html", "partials/my_submissions_body.html"
    )
    return templates.TemplateResponse(
        request,
        template,
        {
            "view": "grid" if view == "grid" else "list",
            "groups": data.GROUPS,
            "my_submissions_count": data.total_submissions(),
            "submissions": data.all_submissions(),
        },
    )


@router.get("/research-groups/{group_id}", response_class=HTMLResponse)
def research_group_page(
    request: Request, identity: CurrentIdentity, group_id: int
) -> Response:
    # Static data shaped like the group-scoped API responses.
    if identity is None:
        return _login_redirect(request)

    from zapp_atlas.html import dashboard_placeholder as data

    view = data.get_group_view(group_id)
    if view is None:
        raise HTTPException(status_code=404, detail="Research group not found")
    template = _dash_template(
        request, "dashboard.html", "partials/dashboard_body.html"
    )
    return templates.TemplateResponse(request, template, view)


@router.post("/research-groups", response_class=HTMLResponse)
def create_research_group(
    request: Request,
    identity: CurrentIdentity,
    session: Annotated[Session, Depends(get_session)],
    name: Annotated[str, Form()],
) -> Response:
    # The signed-in caller becomes the group's first admin (create_group).
    if identity is None:
        return _login_redirect(request)

    from zapp_atlas.api.services.research_groups import create_group

    group = create_group(session, name.strip(), identity)
    return _redirect(request, f"/research-groups/{group.id}")


@router.get("/partials/hello", response_class=HTMLResponse)
def hello_partial(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "partials/hello.html")
