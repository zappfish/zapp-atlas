from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from zapp_atlas.api.deps import get_app_settings
from zapp_atlas.auth.deps import CurrentIdentity
from zapp_atlas.html.templating import templates
from zapp_atlas.settings import AppSettings


router = APIRouter(tags=["html"])


@router.get("/", response_class=HTMLResponse)
def index_page(request: Request, view: str = "grid", page: int = 1) -> HTMLResponse:
    # Public phenotype atlas. Static data shaped like the search API response.
    # `view` toggles the results layout between the card grid and a list; the
    # filter UI is presentational — the search endpoint owns the actual query.
    from zapp_atlas.html import home_placeholder as data

    page_view = data.page(page)
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "view": "list" if view == "list" else "grid",
            "title": data.TITLE,
            "description": data.DESCRIPTION,
            "stats": data.ATLAS_STATS,
            "records": page_view["records"],
            "total_results": data.TOTAL_RESULTS,
            "current_page": page_view["current_page"],
            "total_pages": page_view["total_pages"],
            "facets": data.FACETS,
            "active_filters": data.ACTIVE_FILTERS,
            "sort_options": data.SORT_OPTIONS,
        },
    )


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


@router.get("/my-submissions", response_class=HTMLResponse)
def my_submissions_page(request: Request) -> HTMLResponse:
    # Post-login landing. The sidebar renders the group list and total count.
    from zapp_atlas.html import dashboard_placeholder as data

    return templates.TemplateResponse(
        request,
        "my_submissions.html",
        {
            "groups": data.GROUPS,
            "my_submissions_count": data.total_submissions(),
            "submissions": data.all_submissions(),
        },
    )


@router.get("/research-groups/{group_id}", response_class=HTMLResponse)
def research_group_page(request: Request, group_id: int) -> HTMLResponse:
    # Static data shaped like the group-scoped API responses.
    from zapp_atlas.html import dashboard_placeholder as data

    view = data.get_group_view(group_id)
    if view is None:
        raise HTTPException(status_code=404, detail="Research group not found")
    return templates.TemplateResponse(request, "dashboard.html", view)


@router.get("/partials/hello", response_class=HTMLResponse)
def hello_partial(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "partials/hello.html")
