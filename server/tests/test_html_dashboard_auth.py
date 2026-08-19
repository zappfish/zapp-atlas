from __future__ import annotations

from fastapi.testclient import TestClient

GUARDED = ["/my-submissions", "/research-groups/1"]


def _sign_in(client: TestClient) -> None:
    client.app.state.settings.dev_auth = True
    client.post("/auth/dev/login", data={"name": "Ada Lovelace"})


def test_dashboard_pages_redirect_to_login_when_signed_out(client: TestClient) -> None:
    for path in GUARDED:
        res = client.get(path, follow_redirects=False)
        assert res.status_code == 303
        assert res.headers["location"] == "/login"


def test_dashboard_htmx_requests_signal_a_full_page_redirect(client: TestClient) -> None:
    # htmx follows a 3xx into its swap target, so the guard answers an htmx
    # request with HX-Redirect and no body.
    for path in GUARDED:
        res = client.get(path, headers={"HX-Request": "true"}, follow_redirects=False)
        assert res.status_code == 204
        assert res.headers["HX-Redirect"] == "/login"


def test_dashboard_pages_render_when_signed_in(client: TestClient) -> None:
    _sign_in(client)
    for path in GUARDED:
        assert client.get(path).status_code == 200
