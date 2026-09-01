from __future__ import annotations

from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from zapp_atlas.api.deps import get_app_settings, get_session
from zapp_atlas.auth.deps import CurrentIdentity
from zapp_atlas.html import curation_guidelines, dashboard_service
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


def _group_redirect(request: Request, group_id: int, notice: str = "") -> Response:
    # Back to the group page, optionally carrying a notice for a duplicate or
    # other benign conflict so the page can show it instead of an error.
    target = f"/research-groups/{group_id}"
    if notice:
        target += "?" + urlencode({"notice": notice})
    return _redirect(request, target)


def _leading_id(slug: str) -> int | None:
    # A record slug is "<id>-<label>"; the leading integer is the real id and
    # the label is cosmetic. Returns None when the slug does not start with one.
    head = slug.split("-", 1)[0]
    return int(head) if head.isdigit() else None


_CHEMICAL_EXISTS = "Chemical already exists in this research group."


@router.get("/", response_class=HTMLResponse)
def index_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@router.get("/curation-guidelines", response_class=HTMLResponse)
def curation_guidelines_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "curation_guidelines.html",
        {
            "groups": curation_guidelines.GROUPS,
            "entry_count": curation_guidelines.entry_count(),
        },
    )


@router.get("/downloads", response_class=HTMLResponse)
def downloads_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "coming_soon.html", {"heading": "Downloads"}
    )


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


def _dash_template(request: Request, full: str, body: str) -> str:
    # Sidebar navigation is an htmx request: return just the swapped #dash-body.
    # A direct load returns the full page.
    return body if request.headers.get("HX-Request") else full


@router.get("/my-submissions", response_class=HTMLResponse)
def my_submissions_page(
    request: Request,
    identity: CurrentIdentity,
    session: Annotated[Session, Depends(get_session)],
    view: str = "list",
) -> Response:
    # Post-login landing: the sidebar lists the user's groups.
    if identity is None:
        return _login_redirect(request)

    from zapp_atlas.api.services.research_groups import list_groups_for

    template = _dash_template(
        request, "my_submissions.html", "partials/my_submissions_body.html"
    )
    return templates.TemplateResponse(
        request,
        template,
        {
            "view": "grid" if view == "grid" else "list",
            "groups": list_groups_for(session, identity),
            "my_submissions_count": 0,
            "submissions": [],
        },
    )


@router.get("/research-groups/{group_id}", response_class=HTMLResponse)
def research_group_page(
    request: Request,
    identity: CurrentIdentity,
    session: Annotated[Session, Depends(get_session)],
    group_id: int,
    notice: str = "",
) -> Response:
    if identity is None:
        return _login_redirect(request)

    view = dashboard_service.group_view(session, identity, group_id)
    if view is None:
        raise HTTPException(status_code=404, detail="Research group not found")
    view["notice"] = notice
    template = _dash_template(
        request, "dashboard.html", "partials/dashboard_body.html"
    )
    return templates.TemplateResponse(request, template, view)


@router.get(
    "/research-groups/{group_id}/fish-tank/{entry_slug}",
    response_class=HTMLResponse,
)
def fish_detail_page(
    request: Request,
    identity: CurrentIdentity,
    session: Annotated[Session, Depends(get_session)],
    group_id: int,
    entry_slug: str,
) -> Response:
    if identity is None:
        return _login_redirect(request)

    entry_id = _leading_id(entry_slug)
    if entry_id is None:
        raise HTTPException(status_code=404, detail="Fish line not found")
    view = dashboard_service.fish_detail_view(
        session, identity, group_id, entry_id
    )
    if view is None:
        raise HTTPException(status_code=404, detail="Fish line not found")
    template = _dash_template(
        request, "fish_detail.html", "partials/fish_detail_body.html"
    )
    return templates.TemplateResponse(request, template, view)


@router.get(
    "/research-groups/{group_id}/chemical-cabinet/{entry_slug}",
    response_class=HTMLResponse,
)
def chemical_detail_page(
    request: Request,
    identity: CurrentIdentity,
    session: Annotated[Session, Depends(get_session)],
    group_id: int,
    entry_slug: str,
) -> Response:
    if identity is None:
        return _login_redirect(request)

    entry_id = _leading_id(entry_slug)
    if entry_id is None:
        raise HTTPException(status_code=404, detail="Chemical not found")
    view = dashboard_service.chemical_detail_view(
        session, identity, group_id, entry_id
    )
    if view is None:
        raise HTTPException(status_code=404, detail="Chemical not found")
    template = _dash_template(
        request, "chemical_detail.html", "partials/chemical_detail_body.html"
    )
    return templates.TemplateResponse(request, template, view)


@router.post("/research-groups/{group_id}/fish-tank", response_class=HTMLResponse)
def add_fish_line(
    request: Request,
    identity: CurrentIdentity,
    session: Annotated[Session, Depends(get_session)],
    group_id: int,
    zfin_id: Annotated[str, Form()],
    name: Annotated[str, Form()],
) -> Response:
    if identity is None:
        return _login_redirect(request)
    if not dashboard_service.membership(session, identity, group_id):
        raise HTTPException(status_code=404, detail="Research group not found")

    from pydantic import ValidationError

    from zapp_atlas.api.dto import FishRef
    from zapp_atlas.api.services.fish_tank import add_entry

    try:
        fish = FishRef(zfin_id=zfin_id.strip(), name=name.strip())
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail="Invalid ZFIN id") from exc
    try:
        add_entry(session, group_id, fish)
    except HTTPException as exc:
        return _group_redirect(request, group_id, exc.detail)
    return _group_redirect(request, group_id)


@router.post(
    "/research-groups/{group_id}/fish-tank/{entry_id}/delete",
    response_class=HTMLResponse,
)
def delete_fish_line(
    request: Request,
    identity: CurrentIdentity,
    session: Annotated[Session, Depends(get_session)],
    group_id: int,
    entry_id: int,
) -> Response:
    if identity is None:
        return _login_redirect(request)
    if not dashboard_service.membership(session, identity, group_id):
        raise HTTPException(status_code=404, detail="Research group not found")

    from zapp_atlas.api.services.fish_tank import delete_entry

    if not delete_entry(session, group_id, entry_id):
        raise HTTPException(status_code=404, detail="Fish line not found")
    return _redirect(request, f"/research-groups/{group_id}")


@router.post(
    "/research-groups/{group_id}/chemical-cabinet", response_class=HTMLResponse
)
def add_chemical(
    request: Request,
    identity: CurrentIdentity,
    session: Annotated[Session, Depends(get_session)],
    group_id: int,
    chemical_id: Annotated[str, Form()],
) -> Response:
    if identity is None:
        return _login_redirect(request)
    if not dashboard_service.membership(session, identity, group_id):
        raise HTTPException(status_code=404, detail="Research group not found")

    from zapp_atlas.api.services.cabinet import add_entry

    try:
        add_entry(session, group_id, chemical_id.strip())
    except HTTPException as exc:
        return _group_redirect(request, group_id, _CHEMICAL_EXISTS)
    return _group_redirect(request, group_id)


@router.post(
    "/research-groups/{group_id}/chemical-cabinet/{entry_id}/delete",
    response_class=HTMLResponse,
)
def delete_chemical(
    request: Request,
    identity: CurrentIdentity,
    session: Annotated[Session, Depends(get_session)],
    group_id: int,
    entry_id: int,
) -> Response:
    if identity is None:
        return _login_redirect(request)
    if not dashboard_service.membership(session, identity, group_id):
        raise HTTPException(status_code=404, detail="Research group not found")

    from zapp_atlas.api.services.cabinet import delete_entry

    if not delete_entry(session, group_id, entry_id):
        raise HTTPException(status_code=404, detail="Chemical not found")
    return _redirect(request, f"/research-groups/{group_id}")


@router.post(
    "/research-groups/{group_id}/chemical-cabinet/{entry_id}/edit",
    response_class=HTMLResponse,
)
def edit_chemical(
    request: Request,
    identity: CurrentIdentity,
    session: Annotated[Session, Depends(get_session)],
    group_id: int,
    entry_id: int,
    chemical_id: Annotated[str, Form()],
) -> Response:
    if identity is None:
        return _login_redirect(request)
    if not dashboard_service.membership(session, identity, group_id):
        raise HTTPException(status_code=404, detail="Research group not found")

    from zapp_atlas.api.services.cabinet import update_entry

    try:
        updated = update_entry(
            session, group_id, entry_id, chemical_id=chemical_id.strip()
        )
    except HTTPException as exc:
        return _group_redirect(request, group_id, _CHEMICAL_EXISTS)
    if updated is None:
        raise HTTPException(status_code=404, detail="Chemical not found")
    return _group_redirect(request, group_id)


@router.post("/research-groups/{group_id}/members", response_class=HTMLResponse)
def add_group_member(
    request: Request,
    identity: CurrentIdentity,
    session: Annotated[Session, Depends(get_session)],
    group_id: int,
    member: Annotated[str, Form()],
    role: Annotated[str, Form()],
) -> Response:
    if identity is None:
        return _login_redirect(request)

    from zapp_atlas.api.authz import ResearchGroupRoleEnum
    from zapp_atlas.api.dto import MemberIn
    from zapp_atlas.api.services.research_groups import add_member

    membership = dashboard_service.membership(session, identity, group_id)
    # Non-members read as 404; a member who is not an admin is forbidden.
    if membership is None:
        raise HTTPException(status_code=404, detail="Research group not found")
    if membership.role != ResearchGroupRoleEnum.admin.value:
        raise HTTPException(status_code=403, detail="Admins only")

    from pydantic import ValidationError

    try:
        payload = MemberIn(member=member.strip(), role=role)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail="Invalid member") from exc
    try:
        add_member(session, group_id, payload.member, payload.role.value)
    except HTTPException as exc:
        return _group_redirect(request, group_id, exc.detail)
    return _group_redirect(request, group_id)


@router.post(
    "/research-groups/{group_id}/members/{member_id}/remove",
    response_class=HTMLResponse,
)
def remove_group_member(
    request: Request,
    identity: CurrentIdentity,
    session: Annotated[Session, Depends(get_session)],
    group_id: int,
    member_id: int,
) -> Response:
    if identity is None:
        return _login_redirect(request)

    from zapp_atlas.api.authz import ResearchGroupRoleEnum
    from zapp_atlas.api.services.research_groups import remove_member

    membership = dashboard_service.membership(session, identity, group_id)
    if membership is None:
        raise HTTPException(status_code=404, detail="Research group not found")
    if membership.role != ResearchGroupRoleEnum.admin.value:
        raise HTTPException(status_code=403, detail="Admins only")
    if membership.id == member_id:
        raise HTTPException(status_code=403, detail="Cannot remove yourself")

    if not remove_member(session, group_id, member_id):
        raise HTTPException(status_code=404, detail="Membership not found")
    return _redirect(request, f"/research-groups/{group_id}")


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
