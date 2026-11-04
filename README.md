# ZAPP Atlas

API for the [ZAPP zebrafish toxicology atlas](https://zappfish.org/).

FastAPI server backed by the LinkML-generated
[zebrafish-toxicology-atlas-schema](https://github.com/zappfish/zebrafish-toxicology-atlas-schema).
The previous Flask upload endpoint and the first-pass React/Vite UI are
archived under [`legacy/`](legacy/README.md); neither is wired into the
current build.

## Dev quickstart

```sh
just install
just build-client
just extdata           # ontology bundle; needs docker, a few minutes the first time
just dev-api           # http://localhost:8000
```

That serves everything: the HTML pages at `/`, the JSON API at `/api`, the
React editing client at `/edit`, and the ontology files at `/extdata`.

`just extdata` builds the read-only ontology bundle (ZP, ZFA, ChEBI labels)
into `extdata/dist`. The app runs without it, but anything that needs
ontology data won't work: `/extdata` answers 404 and label lookups fall back
to the CURIE. Rebuild it after changing anything in `extdata/`; see
[extdata/README.md](extdata/README.md).

To work on the React client with hot reloading, run `just dev-client` in one
terminal and `just dev-api-hmr` in another, then open
<http://localhost:8000/edit/> — the page comes from FastAPI, not from Vite.

`just test` runs the pytest suite. `just seed` reseeds the dev DB (seeding
also runs automatically on FastAPI startup unless `ZAPP_SKIP_SEED=1`).

See [ARCHITECTURE.md](ARCHITECTURE.md) for how the two surfaces fit together,
how the LinkML schema drives both, and how to sign in locally without ORCID
credentials.

## Deploy

Any image build needs the ontology bundle in `extdata/dist`, so run
`just extdata` first. The deploy workflows fetch or build it themselves.

- **Fly.io** — `fly deploy` (uses the top-level `Dockerfile` + `fly.toml`).
- **GCP Cloud Run** — `just gcp-ship` builds, pushes, and deploys with a
  GCS-backed volume for the SQLite DB.
