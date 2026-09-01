"""The React client is hosted inside the server-rendered shell.

These cover the seam: the server renders the document, so it has to name the
right script tags for however the client is being run.
"""

import json

import pytest
from fastapi.testclient import TestClient

from zapp_atlas.html.vite import ViteAssetsUnavailable, get_vite_assets


def test_edit_page_renders_inside_the_site_shell(client: TestClient) -> None:
    res = client.get("/edit")

    assert res.status_code == 200
    # The SPA mounts into the shared layout, not a standalone document.
    assert '<div id="root"></div>' in res.text
    assert '<header class="site-header">' in res.text
    assert '<footer class="site-footer">' in res.text
    assert '<link rel="stylesheet" href="/static/css/base.css">' in res.text


def test_edit_page_serves_deep_links(client: TestClient) -> None:
    # Client-side routes must reach the same document so they can be
    # bookmarked and reloaded.
    res = client.get("/edit/studies/1/experiments")

    assert res.status_code == 200
    assert '<div id="root"></div>' in res.text


def test_edit_page_uses_dev_server_when_configured(client: TestClient) -> None:
    client.app.state.settings.vite_dev_server = "http://localhost:5173"

    res = client.get("/edit")

    assert res.status_code == 200
    # The dev client must be present for HMR, and load before the entry.
    assert 'src="http://localhost:5173/edit/@vite/client"' in res.text
    assert 'src="http://localhost:5173/edit/src/main.tsx"' in res.text
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

    assert assets.scripts == ("/edit/assets/main-abc123.js",)
    assert assets.stylesheets == ("/edit/assets/main-def456.css",)
    assert assets.dev_client is None


def test_vite_assets_raise_when_client_is_not_built(tmp_path) -> None:
    with pytest.raises(ViteAssetsUnavailable, match="npm run build"):
        get_vite_assets(tmp_path)


def test_edit_page_explains_how_to_build_when_unavailable(tmp_path) -> None:
    from fastapi import FastAPI

    from zapp_atlas.api.deps import get_app_settings
    from zapp_atlas.html.edit_router import make_edit_router
    from zapp_atlas.settings import AppSettings

    # An app whose client has never been built and has no dev server.
    app = FastAPI()
    app.include_router(make_edit_router(tmp_path))
    app.dependency_overrides[get_app_settings] = lambda: AppSettings(
        vite_dev_server=""
    )

    res = TestClient(app).get("/edit")

    # A missing build is a setup problem, not a 404 — say so.
    assert res.status_code == 503
    assert "npm run build" in res.text
    assert "ZAPP_VITE_DEV_SERVER" in res.text
