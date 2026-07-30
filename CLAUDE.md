# ZAPP Atlas

**Read [ARCHITECTURE.md](ARCHITECTURE.md) first.** It covers how the two
surfaces fit together, how the LinkML schema drives both, and the routing map.
This file is only the things that are easy to get wrong.

## Commands

```sh
just install       # deps for both halves; creates server/.env if absent
just dev-api       # everything on :8000 (HTML, /api, /edit) — Python and
                   # templates hot-reload; the React client does not
just dev-client    # Vite module server on :5173, for React work
just dev-api-hmr   # run alongside dev-client, then open :8000/edit/ — NOT :5173
just test          # pytest
just build-client  # emit client/dist
just seed          # reseed the dev database
```

Client lint/build: `cd client && npm run lint` / `npm run build`.

## Conventions

**Generated code is never hand-edited.** The LinkML schema at
`server/src/zapp_atlas/schema/zebrafish_toxicology_atlas_schema.yaml` is the
single source of truth for the Pydantic models, the SQLAlchemy tables, the
client's TypeScript types, and the client's JSON Schema. Edit the YAML and run
`cd server && make schema`. Generated files carry a `DO NOT EDIT` header.

**All HTML lives in Jinja templates.** Every document and fragment the app
returns — pages, htmx partials, error states, and the React client's host
document — renders through the shared environment in `html/templating.py`, from
`html/templates/`. Do not build HTML strings in Python: markup belongs where it
can be edited without touching a route.

**The React client renders inside the server-rendered shell.** FastAPI serves
the `/edit` document from `templates/edit.html`, which extends `base.html`, so
React mounts into `#root` and inherits the site header, nav, footer, and
stylesheet. `client/` has no `index.html`; its build is asset-only plus a Vite
manifest, which `html/vite.py` reads. Consequences worth remembering:

- In `create_app`, the `/edit/assets` mount **must** stay registered before the
  `/edit/{path:path}` catch-all, or the catch-all swallows the asset files.
- Server-rendered styles live in `html/static/css/`, split by concern and
  linked from `base.html`: `base.css` (design tokens, reset, shared bits —
  loads first), `layout.css` (header, nav, footer), and per-page files
  (`login.css`, `dashboard.css`). Add a new page's styles as its own file and
  link it in `base.html`. `client/src/styles.css` is for editor-specific rules
  only.

**`html/` renders documents, `api/` is read-write JSON.** Keep mutations behind
`/api`.

**`legacy/` is archived** and not part of the build. Don't take patterns from it.

## Signing in locally

ORCID needs client credentials. For UI work, set `ZAPP_DEV_AUTH=true` instead:
`/login` grows a form that signs in a fake identity via `POST /auth/dev/login`,
so signed-in states can be built without registering an app. It is off by
default, 404s when off, and **must never be enabled in a deployment** — it hands
a session cookie to anyone who asks.

Pages that need to know who is signed in should depend on `get_current_identity`
(`auth/deps.py`) rather than reading the cookie directly.

## Building the editing form

Start from `client/src/schema/README.md`. It explains how the generated types
and JSON Schema combine into validation, blank instances, and deep updates —
`makeEmpty`, `updateAt`, `Create<T>`/`Draft<T>`, and the Ajv helpers. No
per-entity form code is written by hand.

## Current state

The HTML surface is styled (design tokens, header, footer, login page, and a
signed-in header chip). A shared template context processor exposes the
signed-in identity as `current_identity` to every page. Pages so far: homepage,
login, and a research group dashboard whose fish tank / chemical cabinet /
submissions render from placeholder data (`html/dashboard_placeholder.py`)
until the group-scoped endpoints are wired in. The data form is not built yet.
ORCID establishes an identity but does **not** yet gate `/api` writes.
