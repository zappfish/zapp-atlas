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
│   ├── routers/       studies, experiments, exposures, observations, images
│   └── services/      CRUD business logic per resource
├── db/                Persistence
│   ├── db.py          SQLAlchemy 2.0 engine + session factory
│   ├── init_db.py     table creation
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
| `/api/{studies,experiments,exposures,observations,images}` | `api` routers | JSON CRUD |
| `GET /health` | `main` | `{"status":"ok"}` |

Route order matters in `create_app`: the `/edit/assets` mount is registered
**before** the `/edit/{path:path}` catch-all, which would otherwise swallow
requests for the asset files.

If the client is neither built nor pointed at a dev server, `/edit` returns a
503 page explaining how to start it — a missing build is a setup problem, not a
404.

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
| `schema/_gen/pydantic.py` | `gen-pydantic` | request/response validation |
| `schema/_gen/pydantic_crud.py` | `crud_pydanticgen.py` (custom) | create/read API variants |
| `schema/_gen/sqla.py` | `gen-sqla` | ORM tables |
| `client/src/schema/index.ts` | `gen-typescript` | React app's types |

```sh
cd server && make schema      # regenerate all four after editing the YAML
```

The thin wrappers `schema/{pydantic,pydantic_crud,sqla}.py` re-export the `_gen/`
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
# One-time setup
cd server && uv sync
cd client && npm install
cp server/.env.default server/.env     # then edit as needed

# Working on the HTML pages only
just dev-api                           # http://localhost:8000

# Working on the React editing client (two terminals)
just dev-client                        # Vite module server on :5173
just dev-api-hmr                       # uvicorn, pointed at Vite
#   → open http://localhost:8000/edit/  (NOT :5173)

just test          # pytest
just seed          # reseed the dev database
just build-client  # emit client/dist for production-style serving
```

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
- ORCID login exists but is not yet enforced as an authorization gate on `/api`
  writes — it currently establishes an identity only. Anonymous writes are
  therefore still possible; worth deciding before the form goes live.
