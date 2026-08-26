"""Assert the rendered markup keeps its accessibility hooks — ARIA
attributes, form labels, and image alt text — so they survive refactors."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _sign_in(client: TestClient) -> None:
    client.app.state.settings.dev_auth = True
    client.post(
        "/auth/dev/login",
        data={"name": "Ada Lovelace", "orcid_id": "0000-0001-1111-2222"},
    )


def test_header_menu_button_has_aria_hooks(client: TestClient) -> None:
    # The hamburger toggles the nav, so it must announce its expanded state
    # and point at what it controls.
    res = client.get("/")

    assert 'aria-expanded="false"' in res.text
    assert 'aria-controls="site-nav"' in res.text
    assert 'aria-label="Menu"' in res.text


def test_decorative_logos_have_empty_alt(client: TestClient) -> None:
    # The wordmark next to each logo already names the site, so the image is
    # decorative and must not be announced twice.
    res = client.get("/")

    assert '<img class="site-brand__logo" src="/static/logo-white.svg" alt="">' in res.text
    assert '<img class="site-footer__logo" src="/static/logo-white.svg" alt="">' in res.text


def test_login_form_controls_are_labelled(client: TestClient) -> None:
    res = client.get("/login")

    assert res.status_code == 200
    # The sign-in call to action is a real link with visible text.
    assert "Sign in with ORCID iD" in res.text
    # Decorative icons inside it are hidden from assistive tech.
    assert 'aria-hidden="true"' in res.text


def test_user_menu_button_has_aria_hooks_when_signed_in(client: TestClient) -> None:
    _sign_in(client)

    res = client.get("/")

    # The signed-in chip opens a dropdown; expose that relationship.
    assert 'aria-controls="user-dropdown"' in res.text
    assert 'aria-expanded="false"' in res.text
