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


def _is_member(session: Session, identity, group_id: int) -> bool:
    # Unknown group and non-membership both read as "not a member", so a
    # caller can't probe which groups exist.
    from zapp_atlas.api.authz import orcid_curie
    from zapp_atlas.schema.sqla import ResearchGroup, ResearchGroupMember

    if session.get(ResearchGroup, group_id) is None:
        return False
    return (
        session.query(ResearchGroupMember)
        .filter_by(research_group=group_id, member=orcid_curie(identity.orcid_id))
        .one_or_none()
        is not None
    )


def _group_view(session: Session, identity, group_id: int) -> dict | None:
    """The dashboard context for a group, or None if the caller is not a
    member.
    """
    from zapp_atlas.api.services import cabinet, fish_tank, research_groups
    from zapp_atlas.schema.sqla import ResearchGroup

    if not _is_member(session, identity, group_id):
        return None
    group = session.get(ResearchGroup, group_id)

    tank = fish_tank.list_entries(session, group_id)
    chemicals = cabinet.list_entries(session, group_id)
    groups = research_groups.list_groups_for(session, identity)
    return {
        "groups": groups,
        "my_submissions_count": 0,
        "group": {
            "id": group.id,
            "name": group.name,
            "is_default": False,
            "chemical_count": len(chemicals),
            "fish_line_count": len(tank),
            "submission_count": 0,
        },
        "fish_tank": [
            {
                "name": e.fish.name,
                "zf_id": e.fish.zfin_id,
                "delete_url": f"/research-groups/{group_id}/fish-tank/{e.id}/delete",
            }
            for e in tank
        ],
        "cabinet": [
            {
                "chemical_id": e.chemical_id,
                "edit_url": (
                    f"/research-groups/{group_id}/chemical-cabinet/{e.id}/edit"
                ),
                "delete_url": (
                    f"/research-groups/{group_id}/chemical-cabinet/{e.id}/delete"
                ),
            }
            for e in chemicals
        ],
        "submissions": [],
    }


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
) -> Response:
    if identity is None:
        return _login_redirect(request)

    view = _group_view(session, identity, group_id)
    if view is None:
        raise HTTPException(status_code=404, detail="Research group not found")
    template = _dash_template(
        request, "dashboard.html", "partials/dashboard_body.html"
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
    if not _is_member(session, identity, group_id):
        raise HTTPException(status_code=404, detail="Research group not found")

    from pydantic import ValidationError

    from zapp_atlas.api.dto import FishRef
    from zapp_atlas.api.services.fish_tank import add_entry

    try:
        fish = FishRef(zfin_id=zfin_id.strip(), name=name.strip())
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail="Invalid ZFIN id") from exc
    add_entry(session, group_id, fish)
    return _redirect(request, f"/research-groups/{group_id}")


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
    if not _is_member(session, identity, group_id):
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
    if not _is_member(session, identity, group_id):
        raise HTTPException(status_code=404, detail="Research group not found")

    from zapp_atlas.api.services.cabinet import add_entry

    add_entry(session, group_id, chemical_id.strip())
    return _redirect(request, f"/research-groups/{group_id}")


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
    if not _is_member(session, identity, group_id):
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
    if not _is_member(session, identity, group_id):
        raise HTTPException(status_code=404, detail="Research group not found")

    from zapp_atlas.api.services.cabinet import update_entry

    updated = update_entry(
        session, group_id, entry_id, chemical_id=chemical_id.strip()
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Chemical not found")
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
