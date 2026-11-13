# ZAPP Atlas

API for the [ZAPP zebrafish toxicology atlas](https://zappfish.org/).

FastAPI server backed by the LinkML-generated
[zebrafish-toxicology-atlas-schema](https://github.com/zappfish/zebrafish-toxicology-atlas-schema).
The previous Flask upload endpoint and the first-pass React/Vite UI are
archived under [`legacy/`](legacy/README.md); neither is wired into the
current build.

## Fish picker prototype (this branch)

This branch is the handoff of the fish data-model work (PR #154) plus the
runnable **fish picker prototype**. Start from
[prototypes/fish_picker/README.md](prototypes/fish_picker/README.md); the
short version:

```sh
just install && just fetch-zfin     # one-time; the fetch is ~77 MB of ZFIN files
just fish-picker                    # API on :8000 with the CORS flag the page needs
open prototypes/fish_picker/index.html   # the widget — a file:// page, not a server route
```

The page's header pill must read **"live ZFIN index"**. The embedded-sample
fallback instead means the API isn't up, the fetch is incomplete (10 files
expected in `server/src/zapp_atlas/db/data/zfin/`), or the server was started
without the CORS flag — plain `just dev-api` won't do.

## Dev quickstart

```sh
just install
just build-client
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
