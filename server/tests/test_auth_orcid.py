from __future__ import annotations

import json
from typing import Self
from unittest.mock import patch
from urllib.error import URLError
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, inspect, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from zapp_atlas.auth.models import OrcidIdentity
from zapp_atlas.auth.services import (
    ORCID_AUTH_COOKIE,
    ORCID_STATE_COOKIE,
    fetch_orcid_public_name,
    prefetch_orcid_identity,
    store_orcid_identity,
)
from zapp_atlas.db import init_db
from zapp_atlas.settings import DEFAULT_ORCID_REDIRECT_URI, AppSettings


def test_login_page_offers_sign_in_when_signed_out(client: TestClient) -> None:
    res = client.get("/login")

    assert res.status_code == 200
    assert "Sign in with ORCID" in res.text
    assert "/auth/orcid/login" in res.text
    # Signing out is meaningless when signed out; don't offer it.
    assert "/auth/orcid/logout" not in res.text
    assert "auth_id=" not in res.text


def test_login_page_shows_the_signed_in_user(client: TestClient) -> None:
    client.app.state.settings.dev_auth = True
    client.post(
        "/auth/dev/login",
        data={"name": "Ada Lovelace", "orcid_id": "0000-0001-1111-2222"},
    )

    res = client.get("/login")

    assert res.status_code == 200
    assert "Ada Lovelace" in res.text
    assert "0000-0001-1111-2222" in res.text
    assert "/auth/orcid/logout" in res.text
    # Already signed in — don't also offer to sign in.
    assert "Sign in with ORCID" not in res.text
    assert "/auth/dev/login" not in res.text
    # The state is in the page itself, not fetched afterwards.
    assert 'hx-get="/auth/orcid/status"' not in res.text


def test_orcid_login_redirects_to_authorize(client: TestClient) -> None:
    client.app.state.settings.orcid_client_id = "APP-123"
    client.app.state.settings.orcid_client_secret = "secret"
    client.app.state.settings.orcid_redirect_uri = DEFAULT_ORCID_REDIRECT_URI

    res = client.get("/auth/orcid/login", follow_redirects=False)

    assert res.status_code == 307
    assert ORCID_STATE_COOKIE in res.cookies
    location = res.headers["location"]
    parsed = urlparse(location)
    query = parse_qs(parsed.query)
    assert parsed.scheme == "https"
    assert parsed.netloc == "orcid.org"
    assert parsed.path == "/oauth/authorize"
    assert query["client_id"] == ["APP-123"]
    assert query["response_type"] == ["code"]
    assert query["scope"] == ["/authenticate"]
    assert query["redirect_uri"] == [DEFAULT_ORCID_REDIRECT_URI]
    assert query["state"]


def test_registered_callback_stores_token_and_redirects(client: TestClient) -> None:
    client.app.state.settings.orcid_client_id = "APP-123"
    client.app.state.settings.orcid_client_secret = "secret"

    def fake_exchange(config, code):
        assert code == "oauth-code"
        return {
            "access_token": "stored-access-token",
            "refresh_token": "stored-refresh-token",
            "token_type": "bearer",
            "expires_in": 631138518,
            "scope": "/authenticate",
            "name": "Sofia Garcia",
            "orcid": "0000-0001-2345-6789",
        }

    client.cookies.set(ORCID_STATE_COOKIE, "state-value")

    with patch("zapp_atlas.auth.router.exchange_code_for_token", fake_exchange):
        res = client.get(
            "/registered?code=oauth-code&state=state-value",
            follow_redirects=False,
        )

    assert res.status_code == 303
    assert res.headers["location"] == "/my-submissions"
    assert ORCID_AUTH_COOKIE in res.cookies

    status_res = client.get("/auth/orcid/status")
    assert status_res.status_code == 200
    assert "Sofia Garcia" in status_res.text
    assert "0000-0001-2345-6789" in status_res.text
    assert "stored-access-token" not in status_res.text
    assert "stored-refresh-token" not in status_res.text


def test_registered_callback_rejects_state_mismatch(
    client: TestClient,
) -> None:
    client.app.state.settings.orcid_client_id = "APP-123"
    client.app.state.settings.orcid_client_secret = "secret"
    client.cookies.set(ORCID_STATE_COOKIE, "expected")

    res = client.get("/registered?code=oauth-code&state=actual")

    assert res.status_code == 400
    assert "state did not match" in res.text


def test_dev_login_is_absent_by_default(client: TestClient) -> None:
    assert client.app.state.settings.dev_auth is False

    assert "/auth/dev/login" not in client.get("/login").text

    res = client.post("/auth/dev/login", follow_redirects=False)
    assert res.status_code == 404
    assert ORCID_AUTH_COOKIE not in res.cookies


def test_dev_login_signs_in_when_enabled(client: TestClient) -> None:
    client.app.state.settings.dev_auth = True

    assert "/auth/dev/login" in client.get("/login").text

    res = client.post(
        "/auth/dev/login",
        data={"name": "Josiah Carberry", "orcid_id": "0000-0002-1825-0097"},
        follow_redirects=False,
    )

    assert res.status_code == 303
    assert res.headers["location"] == "/my-submissions"
    assert ORCID_AUTH_COOKIE in res.cookies

    status_res = client.get("/auth/orcid/status")
    assert status_res.status_code == 200
    assert "Josiah Carberry" in status_res.text
    assert "0000-0002-1825-0097" in status_res.text


def test_orcid_logout_clears_auth_cookie(client: TestClient) -> None:
    client.cookies.set(ORCID_AUTH_COOKIE, "auth-id")

    res = client.post("/auth/orcid/logout", follow_redirects=False)

    assert res.status_code == 303
    assert res.headers["location"] == "/login"
    assert res.cookies.get(ORCID_AUTH_COOKIE) is None


def test_store_orcid_identity_updates_existing_identity() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    init_db(engine)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        first = store_orcid_identity(
            session,
            {
                "access_token": "first-access-token",
                "refresh_token": "first-refresh-token",
                "token_type": "bearer",
                "expires_in": 100,
                "scope": "/authenticate",
                "name": "Sofia Garcia",
                "orcid": "0000-0001-2345-6789",
            },
        )
        second = store_orcid_identity(
            session,
            {
                "access_token": "second-access-token",
                "refresh_token": "second-refresh-token",
                "token_type": "bearer",
                "expires_in": 200,
                "scope": "/authenticate",
                "name": "Dr. Sofia Garcia",
                "orcid": "0000-0001-2345-6789",
            },
        )

        identity_count = session.scalar(select(func.count()).select_from(OrcidIdentity))

    assert second.id == first.id
    assert identity_count == 1
    assert second.name == "Dr. Sofia Garcia"


def _memory_sessionmaker() -> sessionmaker:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    init_db(engine)
    return sessionmaker(bind=engine)


def test_prefetched_name_survives_logins(monkeypatch) -> None:
    monkeypatch.setattr(
        "zapp_atlas.auth.services.fetch_orcid_public_name",
        lambda *args, **kwargs: "Public Name",
    )
    Session = _memory_sessionmaker()

    with Session() as session:
        prefetched = prefetch_orcid_identity(session, "0000-0001-2345-6789")
        assert prefetched.name == "Public Name"

        # A login whose token payload lacks a name must not clobber the
        # prefetched one with null ...
        logged_in = store_orcid_identity(session, {"orcid": "0000-0001-2345-6789"})
        assert logged_in.id == prefetched.id
        assert logged_in.name == "Public Name"

        # ... a login that does carry a name is authoritative ...
        renamed = store_orcid_identity(
            session, {"orcid": "0000-0001-2345-6789", "name": "Real Name"}
        )
        assert renamed.name == "Real Name"

        # ... and a later prefetch (say, added to a second group) keeps it.
        assert prefetch_orcid_identity(session, "0000-0001-2345-6789").name == "Real Name"

        count = session.scalar(select(func.count()).select_from(OrcidIdentity))
    assert count == 1


class _FakeResponse:
    def __init__(self, payload: object) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        return None


def _fetch_against(monkeypatch, payload: object, base_url: str) -> tuple[str | None, str | None]:
    """Run the real fetch_orcid_public_name against a canned response."""
    seen: dict[str, str] = {}

    def fake_urlopen(request, timeout=None):
        seen["url"] = request.full_url
        return _FakeResponse(payload)

    monkeypatch.setattr("zapp_atlas.auth.services.urlopen", fake_urlopen)
    settings = AppSettings(orcid_base_url=base_url, _env_file=None)
    return fetch_orcid_public_name("0000-0002-1825-0097", settings), seen.get("url")


def test_fetch_public_name_parses_the_record(monkeypatch) -> None:
    # The published credit name wins when present ...
    payload = {
        "name": {
            "credit-name": {"value": "J. S. Carberry"},
            "given-names": {"value": "Josiah"},
            "family-name": {"value": "Carberry"},
        }
    }
    name, url = _fetch_against(monkeypatch, payload, "https://orcid.org")
    assert name == "J. S. Carberry"
    assert url == "https://pub.orcid.org/v3.0/0000-0002-1825-0097/personal-details"

    # ... otherwise given + family; the sandbox site maps to its public host.
    payload = {"name": {"given-names": {"value": "Josiah"}, "family-name": {"value": "Carberry"}}}
    name, url = _fetch_against(monkeypatch, payload, "https://sandbox.orcid.org")
    assert name == "Josiah Carberry"
    assert url == "https://pub.sandbox.orcid.org/v3.0/0000-0002-1825-0097/personal-details"


def test_fetch_public_name_returns_none_on_failure(monkeypatch) -> None:
    # A private record publishes no name block.
    name, _ = _fetch_against(monkeypatch, {"name": None}, "https://orcid.org")
    assert name is None

    # Network trouble is swallowed; the caller falls back to the bare ORCID.
    def failing_urlopen(request, timeout=None):
        raise URLError("no route to host")

    monkeypatch.setattr("zapp_atlas.auth.services.urlopen", failing_urlopen)
    assert fetch_orcid_public_name("0000-0002-1825-0097", AppSettings(_env_file=None)) is None


def test_orcid_identity_table_is_registered_with_init_db() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    init_db(engine)

    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns("OrcidIdentity")}
    indexes = inspector.get_indexes("OrcidIdentity")

    assert "OrcidIdentity" in inspector.get_table_names()
    assert "orcid_id" in columns
    assert any(index["unique"] and index["column_names"] == ["orcid_id"] for index in indexes)
    assert "access_token" not in columns
    assert "refresh_token" not in columns
