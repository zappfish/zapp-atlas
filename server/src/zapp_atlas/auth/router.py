from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from zapp_atlas.api.deps import get_app_settings, get_session
from zapp_atlas.auth.services import (
    ORCID_STATE_COOKIE,
    OrcidConfigError,
    OrcidTokenExchangeError,
    build_authorization_url,
    exchange_code_for_token,
    get_orcid_config,
    get_orcid_token,
    make_state,
    state_matches,
    store_orcid_token,
)
from zapp_atlas.settings import AppSettings
from zapp_atlas.html.router import _escape


router = APIRouter(tags=["auth"])


def _error_page(message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> HTMLResponse:
    return HTMLResponse(
        f"""<!doctype html>
<html lang="en">
  <head><title>ORCID Login Error</title></head>
  <body>
    <main>
      <h1>ORCID login failed</h1>
      <p>{_escape(message)}</p>
      <p><a href="/login">Return to login</a></p>
    </main>
  </body>
</html>""",
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
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[AppSettings, Depends(get_app_settings)],
    code: Annotated[str | None, Query()] = None,
    state: Annotated[str | None, Query()] = None,
    error: Annotated[str | None, Query()] = None,
    error_description: Annotated[str | None, Query()] = None,
    expected_state: Annotated[str | None, Cookie(alias=ORCID_STATE_COOKIE)] = None,
):
    if error:
        return _error_page(error_description or error)
    if not code:
        return _error_page("ORCID did not return an authorization code.")
    if not state or not expected_state or not state_matches(state, expected_state):
        return _error_page("ORCID login state did not match. Please try again.")

    try:
        config = get_orcid_config(settings)
        token_payload = exchange_code_for_token(config, code)
        token = store_orcid_token(session, token_payload)
    except (OrcidConfigError, OrcidTokenExchangeError) as exc:
        return _error_page(str(exc), status.HTTP_502_BAD_GATEWAY)

    response = RedirectResponse(
        f"/login?auth_id={token.id}", status_code=status.HTTP_303_SEE_OTHER
    )
    response.delete_cookie(ORCID_STATE_COOKIE)
    return response


@router.get("/auth/orcid/status/{auth_id}", response_class=HTMLResponse)
def orcid_status(
    auth_id: str,
    session: Annotated[Session, Depends(get_session)],
) -> HTMLResponse:
    token = get_orcid_token(session, auth_id)
    if token is None:
        return HTMLResponse(
            "<p>No ORCID login was found for this callback.</p>",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    display_name = _escape(token.name) or "ORCID user"
    orcid_id = _escape(token.orcid_id)
    return HTMLResponse(
        f"<p><strong>Signed in as {display_name}</strong><br>ORCID iD {orcid_id}</p>"
    )
