"""Locating the built React assets for the editing client.

The SPA renders inside the server-rendered shell, so the server — not Vite —
emits the document. That means the server has to name the script and
stylesheet itself, and where those live depends on how the app is running:

    dev    ZAPP_VITE_DEV_SERVER is set; load modules straight from the Vite
           dev server so HMR works. Vite injects the CSS itself.
    built  read client/dist/.vite/manifest.json to resolve the hashed
           filenames produced by `npm run build`.
"""

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


# Matches `rollupOptions.input` in client/vite.config.ts.
ENTRY = "src/main.tsx"


class ViteAssetsUnavailable(RuntimeError):
    """The client has not been built and no dev server is configured."""


@dataclass(frozen=True)
class ViteAssets:
    """The tags edit.html needs in order to boot the React app."""

    scripts: tuple[str, ...] = ()
    stylesheets: tuple[str, ...] = ()
    # The dev client must load before the entry module for HMR to attach.
    dev_client: str | None = field(default=None)


def dev_assets(dev_server_url: str) -> ViteAssets:
    base = dev_server_url.rstrip("/")
    return ViteAssets(
        scripts=(f"{base}/edit/{ENTRY}",),
        # In dev, Vite injects styles at runtime; there is no stylesheet yet.
        stylesheets=(),
        dev_client=f"{base}/edit/@vite/client",
    )


def built_assets(dist_dir: Path) -> ViteAssets:
    manifest_path = dist_dir / ".vite" / "manifest.json"
    if not manifest_path.is_file():
        raise ViteAssetsUnavailable(
            f"No Vite manifest at {manifest_path}. "
            "Run `npm run build` in client/, or set ZAPP_VITE_DEV_SERVER."
        )

    manifest = json.loads(manifest_path.read_text())
    entry = manifest.get(ENTRY)
    if entry is None:
        raise ViteAssetsUnavailable(
            f"Vite manifest at {manifest_path} has no entry for {ENTRY!r}."
        )

    # Asset URLs are the build's `base` ('/edit/') joined to the manifest path.
    return ViteAssets(
        scripts=(f"/edit/{entry['file']}",),
        stylesheets=tuple(f"/edit/{href}" for href in entry.get("css", ())),
    )


@lru_cache(maxsize=8)
def _cached_built_assets(dist_dir: Path, _mtime: float) -> ViteAssets:
    # _mtime is part of the cache key only, so a rebuild is picked up without
    # restarting the server.
    return built_assets(dist_dir)


def get_vite_assets(dist_dir: Path, dev_server_url: str = "") -> ViteAssets:
    if dev_server_url:
        return dev_assets(dev_server_url)

    manifest_path = dist_dir / ".vite" / "manifest.json"
    if not manifest_path.is_file():
        raise ViteAssetsUnavailable(
            f"No Vite manifest at {manifest_path}. "
            "Run `npm run build` in client/, or set ZAPP_VITE_DEV_SERVER."
        )
    return _cached_built_assets(dist_dir, manifest_path.stat().st_mtime)
