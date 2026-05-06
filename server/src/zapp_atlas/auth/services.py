from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from sqlalchemy import select
from sqlalchemy.orm import Session

from zapp_atlas.auth.models import OrcidIdentity
from zapp_atlas.settings import AppSettings, load_settings


ORCID_STATE_COOKIE = "zapp_orcid_state"
ORCID_AUTH_COOKIE = "zapp_orcid_auth"


class OrcidConfigError(RuntimeError):
    pass


class OrcidTokenExchangeError(RuntimeError):
    pass


@dataclass(frozen=True)
class OrcidConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    base_url: str

    @property
    def authorize_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/oauth/authorize"

    @property
    def token_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/oauth/token"


def get_orcid_config(settings: AppSettings | None = None) -> OrcidConfig:
    settings = settings or load_settings()
    client_id = settings.orcid_client_id
    client_secret = settings.orcid_client_secret
    if not client_id or not client_secret:
        raise OrcidConfigError(
            "ZAPP_ORCID_CLIENT_ID and ZAPP_ORCID_CLIENT_SECRET must be set"
        )
    return OrcidConfig(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=settings.orcid_redirect_uri,
        base_url=settings.orcid_base_url,
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


def store_orcid_identity(session: Session, payload: dict[str, Any]) -> OrcidIdentity:
    orcid_id = payload.get("orcid")
    if not orcid_id:
        raise OrcidTokenExchangeError("ORCID token response was missing identity")

    identity = session.scalar(
        select(OrcidIdentity)
        .where(OrcidIdentity.orcid_id == orcid_id)
        .order_by(OrcidIdentity.created_at)
    )
    if identity is None:
        identity = OrcidIdentity(orcid_id=orcid_id)
        session.add(identity)

    identity.name = payload.get("name")

    session.commit()
    session.refresh(identity)
    return identity


def get_orcid_identity(session: Session, auth_id: str) -> OrcidIdentity | None:
    return session.get(OrcidIdentity, auth_id)
