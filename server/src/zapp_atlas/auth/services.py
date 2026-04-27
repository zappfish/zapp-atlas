from __future__ import annotations

import json
import os
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from sqlalchemy.orm import Session

from zapp_atlas.auth.models import OrcidAuthToken


ORCID_STATE_COOKIE = "zapp_orcid_state"
DEFAULT_ORCID_BASE_URL = "https://orcid.org"
DEFAULT_ORCID_REDIRECT_URI = "http://127.0.0.1:8000/registered"


class OrcidConfigError(RuntimeError):
    pass


class OrcidTokenExchangeError(RuntimeError):
    pass


@dataclass(frozen=True)
class OrcidConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    base_url: str = DEFAULT_ORCID_BASE_URL

    @property
    def authorize_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/oauth/authorize"

    @property
    def token_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/oauth/token"


def get_orcid_config() -> OrcidConfig:
    client_id = os.getenv("ORCID_CLIENT_ID", "").strip()
    client_secret = os.getenv("ORCID_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise OrcidConfigError("ORCID_CLIENT_ID and ORCID_CLIENT_SECRET must be set")
    return OrcidConfig(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=os.getenv("ORCID_REDIRECT_URI", DEFAULT_ORCID_REDIRECT_URI).strip(),
        base_url=os.getenv("ORCID_BASE_URL", DEFAULT_ORCID_BASE_URL).strip(),
    )


def make_state() -> str:
    return secrets.token_urlsafe(32)


def state_matches(left: str, right: str) -> bool:
    return secrets.compare_digest(left, right)


def build_authorization_url(config: OrcidConfig, state: str) -> str:
    query = urlencode(
        {
            "client_id": config.client_id,
            "response_type": "code",
            "scope": "/authenticate",
            "redirect_uri": config.redirect_uri,
            "state": state,
        }
    )
    return f"{config.authorize_url}?{query}"


def exchange_code_for_token(config: OrcidConfig, code: str) -> dict[str, Any]:
    form = urlencode(
        {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": config.redirect_uri,
        }
    ).encode("utf-8")
    request = Request(
        config.token_url,
        data=form,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise OrcidTokenExchangeError(
            f"ORCID token endpoint returned {exc.code}: {detail}"
        ) from exc
    except (OSError, URLError, json.JSONDecodeError) as exc:
        raise OrcidTokenExchangeError("Could not exchange ORCID authorization code") from exc


def store_orcid_token(session: Session, payload: dict[str, Any]) -> OrcidAuthToken:
    orcid_id = payload.get("orcid")
    access_token = payload.get("access_token")
    if not orcid_id or not access_token:
        raise OrcidTokenExchangeError("ORCID token response was missing identity or token")

    expires_in = payload.get("expires_in")
    expires_at = None
    if isinstance(expires_in, int):
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)

    row = OrcidAuthToken(
        orcid_id=orcid_id,
        name=payload.get("name"),
        access_token=access_token,
        refresh_token=payload.get("refresh_token"),
        token_type=payload.get("token_type"),
        scope=payload.get("scope"),
        expires_in=expires_in if isinstance(expires_in, int) else None,
        expires_at=expires_at,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def get_orcid_token(session: Session, auth_id: str) -> OrcidAuthToken | None:
    return session.get(OrcidAuthToken, auth_id)

