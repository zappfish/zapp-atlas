from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import StaticPool

from zapp_atlas.auth.services import ORCID_STATE_COOKIE
from zapp_atlas.db import init_db


def test_login_page_renders(client: TestClient) -> None:
    res = client.get("/login")

    assert res.status_code == 200
    assert "Sign in with ORCID" in res.text
    assert "/auth/orcid/login" in res.text


def test_orcid_login_redirects_to_authorize(
    client: TestClient, monkeypatch
) -> None:
    monkeypatch.setenv("ORCID_CLIENT_ID", "APP-123")
    monkeypatch.setenv("ORCID_CLIENT_SECRET", "secret")
    monkeypatch.setenv("ORCID_REDIRECT_URI", "http://127.0.0.1:8000/registered")

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
    assert query["redirect_uri"] == ["http://localhost.localdomain:5000/registered"]
    assert query["state"]


def test_registered_callback_stores_token_and_redirects(
    client: TestClient, monkeypatch
) -> None:
    monkeypatch.setenv("ORCID_CLIENT_ID", "APP-123")
    monkeypatch.setenv("ORCID_CLIENT_SECRET", "secret")

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

    monkeypatch.setattr("zapp_atlas.auth.router.exchange_code_for_token", fake_exchange)
    client.cookies.set(ORCID_STATE_COOKIE, "state-value")

    res = client.get(
        "/registered?code=oauth-code&state=state-value",
        follow_redirects=False,
    )

    assert res.status_code == 303
    assert res.headers["location"].startswith("/login?auth_id=")
    auth_id = parse_qs(urlparse(res.headers["location"]).query)["auth_id"][0]

    status_res = client.get(f"/auth/orcid/status/{auth_id}")
    assert status_res.status_code == 200
    assert "Sofia Garcia" in status_res.text
    assert "0000-0001-2345-6789" in status_res.text
    assert "stored-access-token" not in status_res.text
    assert "stored-refresh-token" not in status_res.text


def test_registered_callback_rejects_state_mismatch(
    client: TestClient, monkeypatch
) -> None:
    monkeypatch.setenv("ORCID_CLIENT_ID", "APP-123")
    monkeypatch.setenv("ORCID_CLIENT_SECRET", "secret")
    client.cookies.set(ORCID_STATE_COOKIE, "expected")

    res = client.get("/registered?code=oauth-code&state=actual")

    assert res.status_code == 400
    assert "state did not match" in res.text


def test_orcid_table_is_registered_with_init_db() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    init_db(engine)

    assert "OrcidAuthToken" in inspect(engine).get_table_names()

