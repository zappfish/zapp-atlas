from __future__ import annotations

from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, inspect, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from zapp_atlas.auth.models import OrcidIdentity
from zapp_atlas.auth.services import (
    ORCID_AUTH_COOKIE,
    ORCID_STATE_COOKIE,
    store_orcid_identity,
)
from zapp_atlas.db import init_db
from zapp_atlas.settings import DEFAULT_ORCID_REDIRECT_URI


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
    assert res.headers["location"] == "/login"
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
    assert res.headers["location"] == "/login"
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


def test_store_orcid_identity_keeps_prefetched_name_when_login_has_none() -> None:
    # An admin adding this person to a group may have pre-populated their
    # identity from the ORCID public API (#142); a token payload that carries
    # no name must not erase that.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    init_db(engine)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        session.add(OrcidIdentity(orcid_id="0000-0001-2345-6789", name="Sofia Garcia"))
        session.commit()

        identity = store_orcid_identity(
            session,
            {
                "access_token": "access-token",
                "token_type": "bearer",
                "scope": "/authenticate",
                "orcid": "0000-0001-2345-6789",
            },
        )

    assert identity.name == "Sofia Garcia"


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
