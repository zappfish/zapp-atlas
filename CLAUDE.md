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
just lint          # ruff check + ruff format --check (no changes written)
just fix           # ruff check --fix + ruff format (applies changes)
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

Two things about that codegen are easy to get wrong:

- **Keep it runnable from a bare `uv sync`.** It once shelled out to `jq`, which
  is not a declared dependency: on a machine without it the recipe truncated the
  client's JSON Schema to zero bytes, and every later run reported "Nothing to be
  done". `.DELETE_ON_ERROR` now removes a half-written target so the next run
  rebuilds it, but the better protection is not reaching for outside tools.
- **`unique_keys` and timestamps are applied after generation.** `gen-sqla`
  renders neither, so `schema/constraints.py` reads them back out of the YAML at
  import and attaches them to the generated tables. Declare them in the schema as
  usual; nothing needs restating in Python. Note that a slot does not always
  become a column of the same name — an inlined slot whose range has an
  identifier becomes `<slot>_<identifier>` (`fish` → `fish_zfin_id`).
- **Class-level `rules` reach neither generated validators nor, unaided, the
  client.** `pydanticgen` does not turn a `rule` into a validator, so anything
  declared that way needs a guard in the service too — raise
  `SchemaRuleViolation` and `create_app` answers 422. And a rule with no
  `preconditions` is emitted as a bare `then` with no `if`, which JSON Schema
  ignores; `schema/json_schema_post.py` hoists those so the client enforces
  them.

**A schema change is not finished until the deployed database can take it.**
`create_all` adds missing tables but never alters an existing one, and the
deployed app keeps its database on a persistent disk — so renaming or adding a
column leaves production asking for columns its file does not have, and every
query on that table fails. `db/migrate.py` runs from `init_db` and closes the
gap: new optional columns are added generically, and anything else (a value
rename, data moved between columns) needs its own idempotent step there. It is
deliberately not a migration framework; if these start accumulating, that is
the signal to adopt Alembic instead of extending it.

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
- Shared design tokens and typography go in `html/static/styles.css` (loaded by
  `base.html`, so it applies to both surfaces). `client/src/styles.css` is for
  editor-specific rules only.

**`html/` renders documents, `api/` is read-write JSON.** Keep mutations behind
`/api`.

**`legacy/` is archived** and not part of the build. Don't take patterns from it.

**Lint and format before committing.** Run `just fix` (or at least `just lint`)
before every commit and **read the ruff output** — don't wave it through. Ruff
uses its full default ruleset (see `server/pyproject.toml` `[tool.ruff]`), so a
warning usually points at a real issue (unused import, blind `except`, a bug
ruff can see); fix the cause rather than reaching for `# noqa`. The QC workflow
runs `ruff check` and `ruff format --check` on every PR and is a required merge
check, so anything you skip locally blocks the PR anyway. Generated `_gen/` code
is excluded and exempt.

## Signing in locally

ORCID needs client credentials. For UI work, set `ZAPP_DEV_AUTH=true` instead:
`/login` grows a button that signs in a fake identity via `POST /auth/dev/login`,
so signed-in states can be built without registering an app. It is off by
default and 404s when off.

**It must never be enabled in production** — it hands a session cookie to anyone
who asks. It *is* enabled deliberately in `fly.preview.toml`, which drives the
per-PR preview apps: ORCID only redirects to pre-registered URIs, so it cannot
work on a per-PR hostname, and a preview is worthless if reviewers have to
bootstrap data by hand before seeing anything. Those apps hold nothing but
throwaway seed data and are destroyed with the PR. Don't "fix" that config.

The fake identity is Josiah Carberry (`0000-0002-1825-0097`) — ORCID's own
canonical sample record, not an invention. Leave it be.

Pages that need to know who is signed in should depend on `get_current_identity`
(`auth/deps.py`) rather than reading the cookie directly.

## Building the editing form

Start from `client/src/schema/README.md`. It explains how the generated types
and JSON Schema combine into validation, blank instances, and deep updates —
`makeEmpty`, `updateAt`, `Create<T>`/`Draft<T>`, and the Ajv helpers. No
per-entity form code is written by hand.

## Current state

The UI is deliberately unstyled: both stylesheets are empty placeholders and the
templates carry no design. The HTML surface has a homepage and a login page; the
submission portal and the data form are not built yet. ORCID establishes an
identity but does **not** yet gate `/api` writes.
