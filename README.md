# ZAPP Atlas

Client and server for the [ZAPP zebrafish toxicology atlas](https://zappfish.org/).

Pre-alpha: a CRUD site for zebrafish toxicology studies (studies →
experiments → exposures → observations, with image attachments). No
authentication yet — anyone can create or edit. The site is driven by
the [`zebrafish-toxicology-atlas-schema`](https://github.com/zappfish/zebrafish-toxicology-atlas-schema)
LinkML schema for the scientific data, with OLS + ZFIN proxies for
ontology autocompletes.

## Dev quickstart

Requires [`just`](https://github.com/casey/just),
[`uv`](https://github.com/astral-sh/uv), and Node 20+.

```bash
# In two terminals:
just dev-api       # FastAPI on :8000 (or $API_PORT)
just dev-client    # Vite on :5173 (or $DEV_PORT)

# Optional: seed a couple of demo studies into the dev DB
just seed
```

Set `API_PORT` / `DEV_PORT` in `.env.local` to override defaults.

## Tests

```bash
just test          # Python / FastAPI tests
just smoke         # Playwright end-to-end (headless)
just smoke-headed  # … with the browser visible
```

The first `just smoke` run needs the Playwright Chromium browser:
`cd client && npx playwright install chromium`.

## Layout

```
server/        FastAPI + SQLAlchemy; schema is a git dependency
  api/
    main.py       app factory, lifespan (init_db + seed)
    routers/      studies, experiments, exposures, observations,
                  images, zfin, ols
    services/     ORM ⇄ Pydantic mapping, ontology resolution
    serializers.py OrmView coercion for Read models
  ontology.py   OLS client (term lookup, ancestors, autocomplete)
  seed.py       dev seed
  storage.py    image blob storage: local fs or any S3-compatible bucket
client/
  src/
    App.tsx       React Router + Layout
    api/          typed fetch wrappers
    components/   Header, Layout, FishAutocomplete, OntologyAutocomplete,
                  PhenotypeModal, (legacy ZappForm/ still present)
    pages/        StudyList, StudyDetail, Study/Experiment/Exposure/
                  Observation form pages
  tests/        Playwright specs
docs/
  plan.md       phased plan for the pre-alpha pass
```

## Deployment

Two deployment paths are wired up:

- **Fly.io** — `fly.toml` + `.github/workflows/fly-deploy.yml` (deploys on
  push to `main`). Bucket storage for images via
  `fly storage create` — sets `AWS_ENDPOINT_URL_S3`, `AWS_ACCESS_KEY_ID`,
  `AWS_SECRET_ACCESS_KEY`, `BUCKET_NAME`.
- **GCP Cloud Run** — see the `gcp-*` recipes in the `Justfile`.

Both use the same multi-stage `Dockerfile` (Vite build → FastAPI runtime).

## Schema dependency

`server/pyproject.toml` pins the schema by git ref. During schema work
you can switch to a local-path editable dep; see `docs/plan.md`.
