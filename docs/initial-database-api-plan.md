# Initial Database API — PR Plan

Branch: `initial-database-api`

## Goal

Land a minimally-scoped FastAPI backend backed by the LinkML schema, cherry-picked from the in-flight `strawperson-pre-alpha-editing-ui` branch (checked out at `../zapp-atlas-strawperson-ui`). That branch tried to do too much at once; this PR pulls just the database/API layer and archives the existing Flask upload endpoint + prototype UI under `legacy/`.

What this PR is **not**: a user-facing UI, ontology autocomplete proxies, or any change to deploy targets beyond what already runs on `main`.

## Source branches

- **This repo (`zapp-atlas`, branch `initial-database-api`)** — Flask `POST /observation` app + legacy React/Vite prototype + GCP/Fly deployment config. A skeletal `server/api/` FastAPI already sits here (studies + experiments routers) but is not wired into the Docker CMD or tested end-to-end.
- **`../zapp-atlas-strawperson-ui` (`strawperson-pre-alpha-editing-ui`)** — fuller FastAPI (studies, experiments, exposures, observations, images, zfin, ols), schema dep bumped to `reachable-from-enums-to-classes`, seed data, storage abstraction, ontology validator, and a React editing UI.

## Scope reductions vs. the strawperson branch

1. **Drop the external autocomplete pass-through routers.** `server/api/routers/zfin.py` and `server/api/routers/ols.py` are not copied over. Nothing in this PR calls out to zfin.org or OLS.
2. **Drop the frontend pass-through.** The FastAPI `spa_catch_all` route and `/assets` `StaticFiles` mount are removed. The API serves API only. No React build is wired into the Docker image for this PR; the frontend stays archived in `legacy/client` (see below).
3. **Drop the new editing UI.** `client/src/pages/*`, routing, autocomplete widgets, Playwright specs — none of that comes over.
4. **Drop `python-multipart` / `boto3` dependencies** unless kept by an in-scope feature (see "Image storage decision" below).

## Decisions (locked in)

1. **No backend ontology validation.** Drop `server/ontology.py` entirely. Strip `_resolve_ontology_term` calls from `services/studies.py` and `services/exposures.py`; exposure `route` / `exposure_type` stored as plain strings (or `None`). Revisit when the UI pass lands.
2. **Keep image storage in scope.** Pull `routers/images.py` + `services/images.py` + `server/storage.py`. Local-filesystem backend only for now; boto3/S3 stays listed as a dep so the cloud path can be flipped on later without a pyproject churn.
3. **Keep Fly.io deploy config.** `fly.toml` stays. We haven't actually exercised it yet; shipping this PR is the first chance to try it.
4. **Remove the frontend from Dockerfile.** Drop stage 1 (`FROM node:20-slim AS frontend`) and the `COPY --from=frontend` line. API-only image.
5. **Seed on startup.** Strawperson runs `seed(session)` during FastAPI `lifespan` unless `ZAPP_SKIP_SEED=1`. Keep as-is so a fresh container has studies to serve.

## Target layout after this PR

```
legacy/
  README.md                 # why this exists; pointers to the new API
  server/
    main.py                 # old Flask app (POST /observation)
    credentials.example.txt
    # (Flask-era db.py/init_db.py NOT moved — the FastAPI uses them)
  client/                   # old Vite prototype (phenodemo.html, src/, etc.)
server/
  api/
    main.py                 # FastAPI entrypoint (from strawperson, trimmed)
    deps.py
    read_models.py
    serializers.py
    routers/
      __init__.py
      studies.py
      experiments.py
      exposures.py
      observations.py
      images.py
    services/
      __init__.py
      studies.py
      experiments.py
      exposures.py
      observations.py
      images.py
  db.py                     # from strawperson (engine/session factory refactor)
  init_db.py                # from strawperson
  seed.py                   # from strawperson
  storage.py                # local-fs backend in use; S3 path dormant
  tests/                    # port the strawperson pytest suite, minus zfin/ols
  pyproject.toml            # schema dep → reachable-from-enums-to-classes
  uv.lock                   # regenerated
Dockerfile                  # CMD unchanged (uvicorn server.api.main:app)
fly.toml                    # unchanged
Justfile                    # keep; drop frontend/playwright recipes not in scope
scripts/                    # keep download_pubchem.py, pubchem_mappings_to_json.py
                            # pull export_seed.py over if keeping seed.py
```

## Step-by-step

### Step 1 — Archive current Flask app + prototype UI under `legacy/`

- `git mv server/main.py legacy/server/main.py`
- `git mv server/credentials.example.txt legacy/server/credentials.example.txt`
- `git mv client legacy/client` — the whole existing Vite prototype (index.html, phenodemo.html, src/, public/, configs).
- **Keep in place** (do not move): `server/db.py`, `server/init_db.py`, `server/__init__.py`, `server/pyproject.toml`, `server/uv.lock`, `server/tests/`, `server/api/` — these are either the FastAPI layer already, or will be overwritten in Step 2.
- Write `legacy/README.md` explaining that these files are preserved for historical reference: the Flask `POST /observation` upload endpoint and the early React/Vite UI prototype. Neither is wired into the current build. Point readers at `server/api/` for the current API.

**Gate:** `git status` shows a clean rename; `just build` still succeeds against the pre-replacement `server/api/` (sanity check — we haven't broken anything yet).

### Step 2 — Replace `server/api/` with the strawperson version (minus pass-through routers)

Copy from `../zapp-atlas-strawperson-ui/server/api/`:

- `main.py` → then edit:
  - Remove `from server.api.routers.zfin import router as zfin_router`
  - Remove `from server.api.routers.ols import router as ols_router`
  - Remove `api.include_router(zfin_router)` / `ols_router`
  - **Remove** the `/assets` StaticFiles mount and the `spa_catch_all` route + the `DIST_DIR` constant they depend on.
  - Keep `/api` prefix on the APIRouter so the URL surface matches the strawperson branch.
- `deps.py`, `read_models.py`, `serializers.py` — copy as-is.
- `routers/__init__.py`, `routers/studies.py`, `routers/experiments.py`, `routers/exposures.py`, `routers/observations.py` — copy as-is.
- `routers/images.py` — copy iff decision 2 = in.
- `services/__init__.py`, `services/studies.py`, `services/experiments.py`, `services/exposures.py`, `services/observations.py` — copy, then strip `_resolve_ontology_term` calls from `studies.py` and `exposures.py` (replace with straight string/None assignment). Also remove the `OntologyValidationError` import + exception handler from `api/main.py`.
- `services/images.py` — copy.

Do **not** copy: `routers/zfin.py`, `routers/ols.py`.

### Step 3 — Replace server module files

From `../zapp-atlas-strawperson-ui/server/`:

- `db.py` → copy (get_engine / get_session_factory refactor).
- `init_db.py` → copy.
- `seed.py` → copy. Keeps the FastAPI lifespan's `seed(session)` call working. If `seed.py` imports from `server/ontology.py` or constructs `ExposureRoute`/`ExposureType` via the ontology client, rewrite those sites to build the ORM rows directly (or skip them) since we're dropping ontology validation.
- `storage.py` → copy.
- `__init__.py` → copy.
- **Do not copy:** `server/ontology.py`.

### Step 4 — Update `server/pyproject.toml`

Diff vs. current:

- Drop `flask` (moved to legacy; no longer imported).
- Drop `httpx` (only `server/ontology.py` used it).
- Bump schema dep: `zebrafish-toxicology-atlas-schema @ git+https://github.com/zappfish/zebrafish-toxicology-atlas-schema.git@reachable-from-enums-to-classes`.
- Add `python-multipart>=0.0.9` (image upload multipart form parsing).
- Add `boto3>=1.35` (local-fs in use now; S3 backend stays wired for later).
- Dev group: drop `respx` (only zfin/ols tests used it; we aren't porting those).
- Regenerate `uv.lock`: `cd server && uv lock`.

### Step 5 — Port the pytest suite

From `../zapp-atlas-strawperson-ui/server/tests/`:

- Copy: `conftest.py`, `test_api_health.py`, `test_api_studies.py`, `test_api_experiments.py`, `test_api_exposures.py`, `test_api_observations.py`, `test_api_deletes.py`, `test_api_full_graph.py`, `test_api_images.py`, `test_db.py`, `test_seed.py`.
- **Do not copy:** `test_api_zfin.py`, `test_api_ols.py`.
- Audit `test_api_exposures.py` + `test_api_studies.py` (+ `test_api_full_graph.py`, `test_seed.py`) for assertions that depend on OLS resolution; relax to "the field round-trips as a plain string" and drop any `respx` fixtures.

**Gate:** `cd server && uv run pytest` green.

### Step 6 — Dockerfile + Justfile trim

- **Dockerfile:** drop the `Stage 1 — Build the React frontend` block, the `ARG VITE_DATA_BASE_URL`, and the `COPY --from=frontend /build/dist/ ./client/dist/` line. Python runtime stage + CMD (`uvicorn server.api.main:app`) stay as-is.
- **Justfile:** keep `dev-api`, `test`, `build`, and the full `gcp-*` block. Remove `dev-client`, `dev` (the dual-terminal reminder), and `gcp-upload-data` (the data files it pushed lived under `client/public/data/`, now archived in `legacy/`). Remove `VITE_DATA_BASE_URL` build-arg lines from `gcp-build` since there's no frontend to pass it to. Pull in `seed` and `export-seed` recipes from the strawperson Justfile so the new seed module is easy to run.
- **fly.toml:** keep untouched; confirm the internal port + uvicorn entrypoint still line up after the Dockerfile trim. Plan to do a real `fly deploy` as the first end-to-end exercise of Fly support.

### Step 7 — README pass

Update the top-level `README.md`:

- One paragraph: "This repo now serves the ZAPP Atlas FastAPI. The previous Flask upload endpoint and React prototype are archived under `legacy/`."
- Dev quickstart: `cd server && uv sync && just dev-api`, then `curl localhost:8000/health`.
- Deployment: point at `just gcp-ship` and `fly deploy`.

### Step 8 — Smoke-test the Docker build + a deploy dry-run

- `just build` locally.
- `docker run --rm -p 8080:8080 zapp-atlas` → `curl localhost:8080/health` → `{"status":"ok"}`.
- `curl localhost:8080/api/studies` → seeded studies come back.
- Fly: this is the first real exercise of Fly support, so go beyond build-only — run `fly deploy` against a dev app and hit `/health` + `/api/studies` on the assigned hostname. Tear it down after.
- GCP: `just gcp-build` but **not** `gcp-deploy` unless the user asks — deploying is a separate step.

## Commit plan

One commit per step where practical, but Steps 2+3+4 likely land together because they're mutually dependent (imports won't resolve otherwise). Suggested commits:

1. `Archive legacy Flask app and Vite prototype under legacy/`
2. `Replace server/api and server/ modules with FastAPI from strawperson branch`
3. `Update pyproject/uv.lock for FastAPI-only deps`
4. `Port pytest suite (minus zfin/ols autocomplete)`
5. `Trim Dockerfile + Justfile to API-only; update README`

## Risks / things to watch

- **Schema dep bump** to `reachable-from-enums-to-classes` introduces composite-PK quirks on `ExposureRoute`/`ExposureType` (see strawperson `docs/plan.md` §Phase 1.5). Since we're not validating/resolving these server-side, the quirk stays latent — but `seed.py` may still construct these classes directly. If so, confirm the composite PK works against SQLite in the ported `test_seed.py` run.
- **Seed on startup** will run against the GCS-mounted SQLite on Cloud Run. If the DB already has rows, `seed()` needs to be idempotent — confirm in `server/seed.py` before shipping (the strawperson file claims to be).
- `_LenientJsonSchema` shim in `api/main.py` — strawperson plan notes it can be removed once the schema bump lands. Sanity check it's still needed after the dep bump; if not, drop it.
- Any test or router referring to image keys needs decision 2 locked in first, or imports will dangle.
