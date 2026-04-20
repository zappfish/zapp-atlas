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
just dev-api           # http://localhost:8000
curl localhost:8000/health
curl localhost:8000/api/studies
```

`just test` runs the pytest suite. `just seed` reseeds the dev DB (seeding
also runs automatically on FastAPI startup unless `ZAPP_SKIP_SEED=1`).

## Deploy

- **Fly.io** — `fly deploy` (uses the top-level `Dockerfile` + `fly.toml`).
- **GCP Cloud Run** — `just gcp-ship` builds, pushes, and deploys with a
  GCS-backed volume for the SQLite DB.
