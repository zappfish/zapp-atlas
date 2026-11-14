# Architecture

ZAPP Atlas is an application for **viewing** and **authoring** zebrafish
toxicological phenotype observations. It has two user-facing surfaces backed by
one FastAPI server and one shared data model:

- **Viewing** — server-rendered HTML, driven by [HTMX](https://htmx.org). Served
  at `/` (and everything that isn't `/edit` or `/api`).
- **Authoring** — a React single-page app, served under `/edit`.

Both halves talk to the same JSON API (`/api/…`) and derive their data shapes
from a single [LinkML](https://linkml.io) schema. Crucially, **both are rendered
into the same HTML shell**: FastAPI serves the document for `/edit` too, so the
React app inherits the site header, nav, footer, and stylesheet rather than
being a separate website that happens to share a domain.

```
                         ┌─────────────────────────────────────────────┐
   browser  ───────────► │  FastAPI app  (server/)                      │
                         │                                               │
    GET /          ──────┼─►  html router  → Jinja2 templates (HTMX)     │
    GET /static/*  ──────┼─►  StaticFiles   → css, vendored htmx.js       │
    GET /edit/*    ──────┼─►  edit router   → edit.html (extends base)    │
    GET /edit/assets/* ──┼─►  StaticFiles   → client/dist/assets (JS/CSS) │
    /auth/*,/registered ─┼─►  auth router   → ORCID OAuth                 │
    /api/*         ──────┼─►  api routers   → JSON CRUD (SQLite)          │
                         └─────────────────────────────────────────────┘
```

## Repository layout

```
zapp-atlas/
├── server/            FastAPI backend + LinkML schema (source of truth)
├── client/            React + Vite + TypeScript editing SPA (served at /edit)
├── extdata/           Offline build of the read-only reference bundle: ontologies
│                      (served at /extdata) and ZFIN's registry of fish lines
├── legacy/            Archived Flask server + first-pass React demo (NOT wired in)
├── scripts/           One-off / operational scripts
├── Justfile           Task runner (dev, test, seed, docker, GCP deploy)
├── Dockerfile         Container build (Fly.io / Cloud Run)
├── fly.toml           Fly.io config
└── README.md
```

The whole tree is a single git repository.

## Backend (`server/`)

A FastAPI app. Python ≥ 3.12, managed with [`uv`](https://docs.astral.sh/uv/);
build backend is Hatchling (`pyproject.toml`). The package is `zapp_atlas`
(under `server/src/`).

```
server/src/zapp_atlas/
├── main.py            create_app(): wires routers, mounts /static and /edit,
│                      lifespan inits DB engine/session + seeds
├── settings.py        AppSettings (pydantic-settings, ZAPP_ env prefix, .env)
├── html/              Server-rendered HTML: every document the app returns
│   ├── router.py      GET / , /login , /partials/hello (Jinja2)
│   ├── edit_router.py GET /edit/* — the host document for the React SPA
│   ├── templating.py  the shared Jinja2 environment (all HTML renders here)
│   ├── vite.py        resolves the client's JS/CSS (dev server or manifest)
│   ├── templates/     base.html (header/content/footer) + pages + partials/
│   └── static/        styles.css (the one stylesheet) + vendored htmx.min.js
├── auth/              ORCID OAuth (login, callback, status, logout)
│   ├── router.py      /auth/orcid/* , /registered
│   ├── services.py    OAuth flow helpers, cookie names
│   └── models.py      OrcidIdentity (SQLAlchemy)
├── api/               Read-write JSON API (mounted under /api)
│   ├── deps.py        get_session / get_app_settings dependencies
│   ├── layout.py      which classes the API saves as a unit (the "levels")
│   ├── tree.py        stores any level from its request body, using layout
│   ├── resources.py   loads the row a path names and checks who may use it
│   ├── authz.py       research-group membership checks
│   ├── models.py      hand-written request/response models (groups, history)
│   ├── openapi.py     writes the OpenAPI document the client's types come from
│   ├── routers/       studies, experiments, exposures, observations, images,
│   │                  research groups, cabinet, fish tank, chemicals
│   │                  (read-only lookups for the chemical picker), and
│   │                  zfin (read-only lookups for the fish picker)
│   └── services/      levels.py (create, replace and delete any level, and
│                      store the revision), plus one module per standalone
│                      resource
├── chem/              NodeNorm client + the ChEBI lookup cache
│                      (read side, and the offline tools that build it)
├── db/                Persistence
│   ├── db.py          SQLAlchemy 2.0 engine + session factory
│   ├── init_db.py     table creation
│   ├── revisions.py   StudyRevision: a copy of a study on every save
│   ├── image_storage.py  local-dir or S3-compatible image storage
│   └── data/          SQLite db + uploads (gitignored)
├── schema/            LinkML schema + generated models (see below)
└── seed.py            example data for the dev database
```

### Request surfaces (routing map)

| Path | Handler | Returns |
|------|---------|---------|
| `GET /` | `html` router | HTML home page (HTMX) |
| `GET /login` | `html` router | HTML login page |
| `GET /partials/*` | `html` router | HTML fragments for HTMX swaps |
| `GET /static/*` | `StaticFiles` | css, vendored htmx |
| `GET /edit/*` | `edit` router | HTML shell hosting the React SPA |
| `GET /edit/assets/*` | `StaticFiles` | the client's built JS/CSS |
| `/auth/orcid/*`, `GET /registered` | `auth` router | ORCID OAuth + status |
| `POST /auth/dev/login` | `auth` router | dev-only fake sign-in (see below) |
| `/api/{studies,experiments,exposures,observations,images}` | `api` routers | the study tree, one resource per level (see below) |
| `/api/studies/{id}/revisions` | `api` studies router | a study's history |
| `/api/research-groups/…` | `api` routers | groups, members, chemical cabinet, fish tank |
| `/api/chemicals/{autocomplete,normalize,vehicle-info}` | `api` chemicals router | read-only chemical lookups (NodeNorm + ChEBI cache) |
| `GET /api/zfin/{wildtypes,status}`, `GET /api/zfin/alleles?q=`, `GET /api/zfin/{alleles,genotypes,fish}/{id}` | `api` zfin router | read-only ZFIN lookups from the bundle's `zfin.db` (503 without it) |
| `POST /api/zfin/resolve` | `api` zfin router | the registered ZFIN genotype and fish a described fish corresponds to |
| `GET /extdata/manifest.json` | `extdata` router | the ontology bundle's hash and versions (not cached) |
| `GET /extdata/<hash>/*` | `extdata` router | ontology files for the client, immutable per hash |
| `GET /health` | `main` | `{"status":"ok"}` |

Route order matters in `create_app`: the `/edit/assets` mount is registered
**before** the `/edit/{path:path}` catch-all, which would otherwise swallow
requests for the asset files.

If the client is neither built nor pointed at a dev server, `/edit` returns a
503 page explaining how to start it — a missing build is a setup problem, not a
404.

### The study tree: one resource per level

A study contains experiments, an experiment contains exposure events, an
exposure event contains observations, and an observation has images. The API
saves each of those **levels** as a unit:

| Level | Create under its parent | Read / replace / delete |
|---|---|---|
| Study | `POST /api/studies` | `/api/studies/{study_id}` |
| Experiment | `POST /api/studies/{study_id}/experiments` | `/api/experiments/{experiment_id}` |
| Exposure event | `POST /api/experiments/{experiment_id}/exposures` | `/api/exposures/{exposure_id}` |
| Observation | `POST /api/exposures/{exposure_id}/observations` | `/api/observations/{observation_id}` |
| Image | `POST /api/observations/{observation_id}/images` (multipart) | `/api/images/{image_id}` |

- A request body carries the level's own fields and the parts it owns, and
  never the level below. An exposure event's body holds its stressors, vehicles
  and regimen. Its observations are saved through their own routes.
- `PUT` replaces the level. A value the body leaves out is cleared. The parts
  the level owns are deleted and recreated, so their ids change on every save.
  The level below is not touched.
- `GET /api/studies/{id}` returns the whole tree. `GET /api/images/{id}`
  returns the file itself.
- `GET /api/studies` lists summaries, optionally for one research group.

`api/layout.py` is the only hand-written statement of this structure. It names
the levels and the classes that have routes of their own. What a level owns,
what it refers to and where it stops are read from the LinkML schema.
`api/tree.py` stores a level by going through those slots, so no slot is named
in Python. The routers are written by hand, but they only name the generated
models and never list fields.

These tests keep the hand-written parts consistent with the schema:

| Problem | Test that catches it |
|---|---|
| A class is added to the schema but not placed in the layout | `tests/test_api_layout.py` |
| A level is missing a route, or a route takes the wrong model | `tests/test_api_routes.py` |
| The save code drops a slot, or leaves rows behind | `tests/test_api_tree.py` (bodies built from the schema) |
| A write route does not require sign-in | `tests/test_api_routes.py` |
| The client's API types are out of date | `tests/test_api_openapi.py`, and a CI check on the generated types |

### Who may read and write

- Writing to any level requires a signed-in member of the research group the
  study belongs to: 401 when signed out, 403 from another group. Every study
  belongs to a group.
- Anyone may read a published study.
- A draft study (`status: draft`), with everything under it including its
  images and history, is visible only to its group. Anyone else gets a 404,
  the same as for a record that does not exist, on write routes too.

A route gets the row it works on from `api/resources.py` (`readable` /
`writable`), which loads it and applies these rules using the study that
contains it. Do not fetch a row in a route directly.

### History

Every create, replace and delete at any level stores a copy of the whole study
in `StudyRevision`, numbered from 1, with the ORCID of whoever made the change.
The table is written by hand in `db/revisions.py` and is not part of the LinkML
schema.

### Persistence

SQLite via SQLAlchemy 2.0. The engine and session factory are created in the
FastAPI lifespan and stored on `app.state`; request handlers get a session via
the `get_session` dependency. Images are stored either on the local filesystem
or in an S3-compatible bucket, selected by settings. All configuration is
environment-driven (`ZAPP_`-prefixed, see `settings.py` / `server/.env.default`).

## Schema and code generation — the single source of truth

The data model is defined once, in LinkML:

```
server/src/zapp_atlas/schema/zebrafish_toxicology_atlas_schema.yaml
```

Everything else is **generated** from it (`server/Makefile`, target `schema`).
Generated files carry a `GENERATED FILE. DO NOT EDIT.` header — edit the YAML
and regenerate, never edit the outputs.

| Output | Generator | Used by |
|--------|-----------|---------|
| `schema/_gen/pydantic_crud.py` | `crud_pydanticgen.py` (custom) | request/response validation: the Pydantic models, plus the API's `Input` / `Read` / `Summary` variants |
| `schema/_gen/sqla.py` | `gen-sqla` | ORM tables |
| `client/src/schema/index.ts` | `gen-typescript` + `typescript_post` | React app's types |

```sh
cd server && make schema      # regenerate these after editing the YAML
```

The custom generator emits three variants of each class. `Input` is what the
API accepts: no `id`, and for a level, no slot for the level below. `Read` is
what it returns, with everything below it. `Summary` is a `Read` without the
level below.

Two more generated files come from the running API, not from the schema:
`client/src/api/openapi.json`, the server's OpenAPI document, and
`client/src/api/openapi.d.ts`, the TypeScript types generated from it. The
client's API types (`client/src/api/types.ts`) are aliases of these.

```sh
just api-types                # regenerate both after changing a route or model
```

The thin wrappers `schema/{pydantic_crud,sqla}.py` re-export the `_gen/`
modules so application code imports a stable path.

### Types across the boundary

The LinkML schema generates **two** client artifacts, and the editing client
uses both:

- `client/src/schema/index.ts` — TypeScript `interface`s and string `enum`s
  (`Study`, `Experiment`, `Fish`, `SeverityEnum`): the compile-time shapes.
- `client/src/schema/schema.json` — the same model as JSON Schema: the runtime
  constraints, compiled with [Ajv](https://ajv.js.org).

On top of those sit a few small generic helpers — no per-entity code is written
by hand:

| File | What it provides |
|------|------------------|
| `document.ts` | `schemaDocument` — `schema.json`, typed once |
| `types.ts` | `Create<T>`, `Update<T>`, `Draft<T>` |
| `variants.ts` | `toInputSchema`, `toDraftSchema`, `normalizeNullableRefs` |
| `validation.ts` | `compile`, `parseAs`, and reference validators |
| `empty.ts` | `makeEmpty` (blank instances), `updateAt` (deep update) |

`client/src/schema/README.md` is the guide for building the form against these,
and is the right starting point for whoever writes the editor.

The server (Pydantic) remains the **authority** on validation — client-side
checks exist to give the form immediate feedback, not to be trusted. Because the
generated interfaces are plain data and field names are already snake_case
(matching the wire format), submitting to the API is just `JSON.stringify(payload)`
— no serialization layer needed.

## Frontend

### Viewing surface (HTMX) — in `server/src/zapp_atlas/html/`

Server-rendered with Jinja2. `base.html` is the single layout
(header / `<main>` content / footer); pages extend it; HTMX fragments live in
`templates/partials/`. The one stylesheet is `static/styles.css` (intentionally
near-empty for now); htmx is vendored in `static/` rather than loaded from a CDN.
This surface needs no build step.

### Authoring surface (React) — `client/`

A from-scratch React 19 + Vite + TypeScript app (modeled on, but not copied
from, the archived `legacy/client`).

```
client/
├── src/
│   ├── main.tsx        the Vite entry; mounts <App/> into #root
│   ├── App.tsx         placeholder shell ("editing UI goes here")
│   ├── styles.css      React-side stylesheet (empty placeholder)
│   └── schema/         generated types + JSON Schema + the form toolkit
├── vite.config.ts      base '/edit/', '@'→src alias, manifest build
├── tsconfig.json       strict; verbatimModuleSyntax + noUnused*; target es2023
├── tsconfig.node.json  Node typing for vite.config.ts (editor only)
└── eslint.config.js    flat config: typescript-eslint + react-hooks/react-refresh
```

**There is no `index.html` here.** The HTML document comes from the server
(`html/templates/edit.html`), in both dev and production, which is what lets the
SPA sit inside the shared shell. Consequences:

- The build is **asset-only**: `rollupOptions.input` is `src/main.tsx`, and
  `build.manifest` is on so the server can find the hashed filenames.
- **`base: '/edit/'`** so those asset URLs resolve under `/edit/assets/`.
- **No `/api` dev proxy is needed** — the page is served from the FastAPI
  origin, so `/api` requests already land on the backend.
- Scripts are `dev`, `build`, `lint`. (`preview` was removed: it served a
  standalone `index.html` that no longer exists.)

## How the two halves wire together

In both modes FastAPI renders the `/edit` document; only the source of the
client's JS/CSS changes. `html/vite.py` decides which:

- **In production:** one FastAPI process serves everything. `npm run build`
  emits `client/dist/assets` plus `.vite/manifest.json`; the server reads the
  manifest for the hashed filenames and serves the files at `/edit/assets`.
- **In development:** two processes, but **you browse only one**. uvicorn serves
  everything on `:8000` — including the `/edit` page. Vite runs on `:5173`
  purely as a module server, and `ZAPP_VITE_DEV_SERVER=http://localhost:5173`
  tells the template to point its `<script>` tags there, so HMR works.

> Open `http://localhost:8000/edit/` — **not** the Vite port. Vite serves no
> HTML; hitting `:5173` directly gets you nothing useful.

## Dev workflow

```sh
# One-time setup: installs both halves and creates server/.env
just install

# Working on the HTML pages only
just dev-api                           # http://localhost:8000

# Working on the React editing client (two terminals)
just dev-client                        # Vite module server on :5173
just dev-api-hmr                       # uvicorn, pointed at Vite
#   → open http://localhost:8000/edit/  (NOT :5173)

just test          # pytest
just e2e           # browser tests (Playwright) against a real server
just seed          # reseed the dev database
just build-client  # emit client/dist for production-style serving
just extdata       # build the ontology bundle into extdata/dist (docker)
```

The reference bundle is built offline from pinned upstream releases, never at
runtime: ZP and ZFA as OBO JSON for the client, `labels.db`, a CURIE ->
label table the server reads through `zapp_atlas/labels.py`, and `zfin.db`,
ZFIN's registered alleles, genotypes, fish and wild-type lines, read through
`zapp_atlas/zfin.py`. Without it the app still runs, but `/extdata` answers
404, label lookups fall back to the CURIE, and `/api/zfin` answers 503. See
[extdata/README.md](extdata/README.md).

### Reference data for the fish picker

The fish form is meant to work by description: the curator picks a wild-type
background, adds alleles by typing a symbol or gene and setting zygosity
(later, injected reagents too), and the form asks ZFIN's registry whether a
fish with exactly that description exists. Ids attach silently; "none
registered" is a real answer. `/api/zfin` serves that flow from `zfin.db`:
`wildtypes` for the background list, `alleles?q=` for the autocomplete,
`resolve` for the match (exact identity, as ZFIN's own records are keyed;
"unknown" zygosity is a value, not a wildcard; several genotypes can match
because ZFIN records a background for only a third of them, and the response
says so), and the by-id routes to show a saved fish's ZFIN details again.
Responses use ZFIN's own vocabulary (SO ids, its zygosity words) rather than
the schema's enums, so the lookup surface does not move when the fish data
model is reworked.

Schema regeneration after editing the LinkML YAML: `cd server && make schema`.

### Signing in locally

ORCID login needs client credentials, which `.env.default` leaves blank. For UI
work you usually don't want to register an app at all — set `ZAPP_DEV_AUTH=true`
and `/login` grows a form that signs in a fake identity via
`POST /auth/dev/login`, so the signed-in states can be built and inspected
without ORCID.

`ZAPP_DEV_AUTH` is off by default, the route 404s when it is off, and it
**must never be enabled in a deployment** — it hands a session cookie to anyone
who asks. To exercise the real flow, register a sandbox app at
`sandbox.orcid.org` and point `ZAPP_ORCID_BASE_URL` at it.

## Deployment

Containerized via `Dockerfile`. Targets: **Fly.io** (`fly.toml`) and **GCP Cloud
Run** (the `gcp-build` / `gcp-deploy` / `gcp-ship` recipes in the `Justfile`,
with the SQLite DB and uploads on a mounted Cloud Storage volume).

The image includes the ontology bundle from `extdata/dist`, so a local image
build needs `just extdata` first. The deploy workflows put it there
themselves: they download the GitHub release `extdata-<hash>` for the
current inputs, or build it, and production deploys publish what they built.
See [extdata/README.md](extdata/README.md#deployment).

## Conventions and current state

- **Generated code is never hand-edited.** Edit the LinkML YAML, run
  `make schema`. Generated files are marked with a `DO NOT EDIT` header.
- **`html` = HTML documents, `api` = read-write JSON.** Keep the boundary clean:
  page rendering in `html/`, mutations behind `/api`.
- **All HTML renders through Jinja.** Every user-visible document and fragment —
  pages, HTMX partials, error states, and the SPA's host document — goes through
  the shared environment in `html/templating.py` and lives under
  `html/templates/`. Don't build HTML strings in Python; markup belongs in
  templates where it can be edited without touching routes.
- **`html/static/styles.css` is the site stylesheet**, loaded by `base.html` and
  therefore in effect on `/edit` too. `client/src/styles.css` is bundled by Vite
  and applies only to the React surface. Shared design tokens, typography, and
  the header/nav/footer belong in the former so both surfaces stay consistent;
  put only editor-specific rules in the latter. Both are currently empty — the
  shell is intentionally unstyled.
- **`legacy/` is archived** and not part of the build.
- Every `/api` write requires a signed-in caller, and writes to the study tree
  require membership of the study's research group. A test fails if a write
  route is added without that.
