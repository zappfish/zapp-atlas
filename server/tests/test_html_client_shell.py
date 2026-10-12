"""The React client is hosted inside the server-rendered shell.

These cover the seam: the server renders the document, so it has to name the
right script tags for however the client is being run.
"""

import json

import pytest
from fastapi.testclient import TestClient

from zapp_atlas.html.vite import ViteAssetsUnavailable, get_vite_assets

GUARDED = ["/my-submissions", "/research-groups/1"]


def _sign_in(client: TestClient) -> None:
    client.app.state.settings.dev_auth = True
    client.post("/auth/dev/login", data={"name": "Ada Lovelace"})


def test_client_routes_redirect_to_login_when_signed_out(client: TestClient) -> None:
    for path in GUARDED:
        res = client.get(path, follow_redirects=False)
        assert res.status_code == 303
        assert res.headers["location"] == "/login"


def test_group_route_serves_the_shell_for_any_group_id(client: TestClient) -> None:
    # The shell does not know who may see a group — it has no data to check
    # against. /api answers that, and returns 404 to a non-member.
    _sign_in(client)

    assert client.get("/research-groups/999999").status_code == 200
    assert client.get("/api/research-groups/999999").status_code == 404


def test_client_route_renders_inside_the_site_shell(client: TestClient) -> None:
    _sign_in(client)

    res = client.get("/my-submissions")

    assert res.status_code == 200
    # React mounts into the shared layout, not a standalone document.
    assert '<div id="root"></div>' in res.text
    # Tag-open matches so the shell's header/footer may carry attributes.
    assert "<header" in res.text
    assert "<footer" in res.text
    assert '<link rel="stylesheet" href="/static/css/base.css">' in res.text


def test_group_route_serves_the_same_shell(client: TestClient) -> None:
    # Every client route returns one document; the path only tells React what
    # to render, so a group page can be bookmarked and reloaded.
    _sign_in(client)

    res = client.get("/research-groups/1")

    assert res.status_code == 200
    assert '<div id="root"></div>' in res.text


def test_client_route_uses_dev_server_when_configured(client: TestClient) -> None:
    _sign_in(client)
    client.app.state.settings.vite_dev_server = "http://localhost:5173"

    res = client.get("/my-submissions")

    assert res.status_code == 200
    # The dev client must be present for HMR, and load before the entry.
    assert 'src="http://localhost:5173/@vite/client"' in res.text
    assert 'src="http://localhost:5173/src/main.tsx"' in res.text
    assert res.text.index("@vite/client") < res.text.index("src/main.tsx")


def test_vite_assets_read_hashed_filenames_from_the_manifest(tmp_path) -> None:
    manifest_dir = tmp_path / ".vite"
    manifest_dir.mkdir()
    (manifest_dir / "manifest.json").write_text(
        json.dumps(
            {
                "src/main.tsx": {
                    "file": "assets/main-abc123.js",
                    "isEntry": True,
                    "css": ["assets/main-def456.css"],
                }
            }
        )
    )

    assets = get_vite_assets(tmp_path)

    assert assets.scripts == ("/assets/main-abc123.js",)
    assert assets.stylesheets == ("/assets/main-def456.css",)
    assert assets.dev_client is None


def test_vite_assets_raise_when_client_is_not_built(tmp_path) -> None:
    with pytest.raises(ViteAssetsUnavailable, match="npm run build"):
        get_vite_assets(tmp_path)


def test_client_route_explains_how_to_build_when_unavailable(tmp_path) -> None:
    from fastapi import FastAPI

    from zapp_atlas.api.deps import get_app_settings
    from zapp_atlas.auth.deps import get_current_identity
    from zapp_atlas.html.client_router import make_client_router
    from zapp_atlas.settings import AppSettings

    # An app whose client has never been built and has no dev server.
    app = FastAPI()
    app.include_router(make_client_router(tmp_path))
    app.dependency_overrides[get_app_settings] = lambda: AppSettings(vite_dev_server="")
    # The route redirects a signed-out caller, which would hide the 503.
    app.dependency_overrides[get_current_identity] = lambda: object()

    res = TestClient(app).get("/my-submissions")

    # A missing build is a setup problem, not a 404 — say so.
    assert res.status_code == 503
    assert "npm run build" in res.text
    assert "ZAPP_VITE_DEV_SERVER" in res.text
