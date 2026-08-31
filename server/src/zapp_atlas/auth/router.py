from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Form,
    HTTPException,
    Query,
    Request,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from zapp_atlas.api.deps import get_app_settings, get_session
from zapp_atlas.auth.services import (
    ORCID_AUTH_COOKIE,
    ORCID_STATE_COOKIE,
    OrcidConfigError,
    OrcidTokenExchangeError,
    build_authorization_url,
    exchange_code_for_token,
    get_orcid_config,
    get_orcid_identity,
    make_state,
    state_matches,
    store_orcid_identity,
)
from zapp_atlas.html.templating import templates
from zapp_atlas.settings import AppSettings

router = APIRouter(tags=["auth"])


def _error_page(
    request: Request,
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "login_error.html",
        {"message": message},
        status_code=status_code,
    )


@router.get("/auth/orcid/login")
def login_with_orcid(
    settings: Annotated[AppSettings, Depends(get_app_settings)],
) -> RedirectResponse:
    try:
        config = get_orcid_config(settings)
    except OrcidConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    state = make_state()
    response = RedirectResponse(build_authorization_url(config, state))
    response.set_cookie(
        ORCID_STATE_COOKIE,
        state,
        max_age=600,
        httponly=True,
        secure=config.redirect_uri.startswith("https://"),
        samesite="lax",
    )
    return response


@router.get("/registered", response_class=HTMLResponse)
def registered_orcid_callback(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[AppSettings, Depends(get_app_settings)],
    code: Annotated[str | None, Query()] = None,
    state: Annotated[str | None, Query()] = None,
    error: Annotated[str | None, Query()] = None,
    error_description: Annotated[str | None, Query()] = None,
    expected_state: Annotated[str | None, Cookie(alias=ORCID_STATE_COOKIE)] = None,
):
    if error:
        return _error_page(request, error_description or error)
    if not code:
        return _error_page(request, "ORCID did not return an authorization code.")
    if not state or not expected_state or not state_matches(state, expected_state):
        return _error_page(request, "ORCID login state did not match. Please try again.")

    try:
        config = get_orcid_config(settings)
        token_payload = exchange_code_for_token(config, code)
        identity = store_orcid_identity(session, token_payload)
    except (OrcidConfigError, OrcidTokenExchangeError) as exc:
        return _error_page(request, str(exc), status.HTTP_502_BAD_GATEWAY)

    response = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        ORCID_AUTH_COOKIE,
        identity.id,
        httponly=True,
        secure=config.redirect_uri.startswith("https://"),
        samesite="lax",
    )
    response.delete_cookie(ORCID_STATE_COOKIE)
    return response


@router.post("/auth/dev/login")
def dev_login(
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[AppSettings, Depends(get_app_settings)],
    name: Annotated[str, Form()] = "Josiah Carberry",
    orcid_id: Annotated[str, Form()] = "0000-0002-1825-0097",
) -> RedirectResponse:
    """Sign in a fake identity without contacting ORCID.

    Local development only, gated behind ZAPP_DEV_AUTH. This exists so the
    signed-in and signed-out states can be designed and tested without ORCID
    credentials; it is an unauthenticated way to obtain a session cookie and
    must never be enabled in a deployment.
    """
    if not settings.dev_auth:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    identity = store_orcid_identity(session, {"orcid": orcid_id, "name": name})

    response = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        ORCID_AUTH_COOKIE,
        identity.id,
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return response


@router.post("/auth/orcid/logout")
def logout_orcid() -> RedirectResponse:
    response = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(ORCID_AUTH_COOKIE)
    return response


@router.get("/auth/orcid/status", response_class=HTMLResponse)
def orcid_status(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    identity_id: Annotated[str | None, Cookie(alias=ORCID_AUTH_COOKIE)] = None,
) -> HTMLResponse:
    identity = None if identity_id is None else get_orcid_identity(session, identity_id)
    missing = identity_id is not None and identity is None

    return templates.TemplateResponse(
        request,
        "partials/orcid_status.html",
        {"identity": identity, "missing": missing},
        status_code=status.HTTP_404_NOT_FOUND if missing else status.HTTP_200_OK,
    )
