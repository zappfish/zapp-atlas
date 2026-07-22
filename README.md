# ZAPP Atlas

API for the [ZAPP zebrafish toxicology atlas](https://zappfish.org/).

FastAPI server backed by the LinkML-generated
[zebrafish-toxicology-atlas-schema](https://github.com/zappfish/zebrafish-toxicology-atlas-schema).
The previous Flask upload endpoint and the first-pass React/Vite UI are
archived under [`legacy/`](legacy/README.md); neither is wired into the
current build.

## Dev quickstart

```sh
cd server && uv sync
cd client && npm install && npm run build
just dev-api           # http://localhost:8000
```

That serves everything: the HTML pages at `/`, the JSON API at `/api`, and the
React editing client at `/edit`.

To work on the React client with hot reloading, run `just dev-client` in one
terminal and `just dev-api-hmr` in another, then open
<http://localhost:8000/edit/> — the page comes from FastAPI, not from Vite.

`just test` runs the pytest suite. `just seed` reseeds the dev DB (seeding
also runs automatically on FastAPI startup unless `ZAPP_SKIP_SEED=1`).

See [ARCHITECTURE.md](ARCHITECTURE.md) for how the two surfaces fit together,
how the LinkML schema drives both, and how to sign in locally without ORCID
credentials.

## Deploy

- **Fly.io** — `fly deploy` (uses the top-level `Dockerfile` + `fly.toml`).
- **GCP Cloud Run** — `just gcp-ship` builds, pushes, and deploys with a
  GCS-backed volume for the SQLite DB.
