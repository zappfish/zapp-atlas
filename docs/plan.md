# ZAPP Atlas POC — Revised Phased Plan (Pass 2)

Supersedes `ui-rework-poc-spec.md` and `plan-connect-form-to-api.md`
(kept as reference; deleted at Phase 7).

## Goal

A deployable UI that matches the existing FastAPI. Anyone can read,
create, and edit studies. **No login.** ORCID auth and per-user
cabinet/tank come in a later pass.

## Principles

- **Schema untouched this pass.** If we hit a genuine gap we'll branch
  the sibling schema repo then — but the default is zero schema
  changes, zero monkeypatching.
- **Red → green gates per phase.** API phases ship pytest first; UI
  phases ship Playwright smoke first. A phase isn't done until the
  tests written at the top of it pass.
- **Burn the first pass.** All untracked first-pass files deleted at
  Phase 0.
- **UI: plain, lightly echoing zappfish.org.** Lato, teal header
  (`#136363`), link color `rgb(0,101,128)`, white page. No component
  library. No design system.
- **Autocomplete-adds-directly.** Fish (ZFIN) lives on the Experiment
  form; Chemical lives on the Exposure form. Selecting a result
  get-or-creates the record and attaches it to the thing you're
  editing — no separate bookmark/tank/cabinet page.

---

## Phases

### Phase 0 — Burn + baseline

- `git clean -fd` on untracked first-pass files (inventory dump saved
  outside the repo first).
- Drop legacy Flask: `server/main.py`, `credentials.example.txt`, the
  `POST /observation` endpoint, the `flask` dep.
- Add Playwright scaffold: `client/tests/`, `playwright.config.ts` with
  a `webServer` block that boots `just dev-api` + `just dev-client`.
  One trivial green spec (visit `/`, page loads).
- Justfile: `just smoke`, `just smoke:headed`, `just seed`.
- **Gate:** `just test` and `just smoke` both green on a fresh clone.

### Phase 1 — API gap check + seed

- Audit existing FastAPI against what the UI will call. Fill only the
  holes the UI genuinely needs:
  - `GET /studies` paginated list (if missing).
  - `GET /studies/{id}` full-graph response (experiments + exposures
    + observations + images).
  - `POST /experiments/{id}/exposures`, `GET/PATCH /exposures/{id}`.
  - `POST /exposures/{id}/observations`, `GET/PATCH /observations/{id}`.
  - `GET /zfin/fish-autocomplete?q=...` — server-side proxy so the
    client never hits zfin.org directly.
  - (Chemical autocomplete: stub endpoint that returns manual-entry
    shape for now; NameRes lands later.)
- `server/seed.py`: a handful of fixed studies/experiments so the UI
  has something to render on first boot. Idempotent. Run via `just
  seed` and on dev lifespan startup.
- **Tests:** pytest for each new/changed endpoint; `respx` mocks zfin.
- **Gate:** `just test` green.

### Phase 2 — API: Image storage

- `Storage` abstraction. Local filesystem backend when
  `AWS_ENDPOINT_URL_S3` absent; S3/Tigris backend otherwise (boto3).
- `POST /images/upload` → returns a key.
- `GET /images/{key}` → file (local) or redirect (cloud).
- Observations reference images by key.
- **Tests:** local fs round-trip; rejects non-images; rejects oversized;
  observation → image linkage persists.
- **Gate:** pytest green.

### Phase 3 — FE: scaffold, routing, layout

- React Router. Top-level layout with `<Header>` (nav only; no user
  affordance).
- `api.ts` fetch wrapper with base URL + error handling.
- Light theme pass: Lato, teal header, accent link color.
- **Smoke:** visit `/`, page renders, nav links work, 404 page works.
- **Gate:** smoke green. Manual: hot reload works.

### Phase 4 — FE: Study list + detail (read-only)

- `StudyListPage` paginated; columns: publication, lab, annotator(s),
  # experiments. Click row → detail.
- `StudyDetailPage` shows full graph — experiments, exposures,
  observations, images.
- **Smoke:** visit `/`, see seeded studies, click one, see the graph
  including an image.
- **Gate:** smoke green.

### Phase 5 — FE: Study + Experiment forms

- `/studies/new`, `/studies/:id/edit` — publication, lab, annotator(s).
- `/studies/:id/experiments/new`, `/experiments/:id/edit` — fish
  (ZFIN autocomplete-adds), rearing, controls.
- Edit buttons visible on detail pages (no ownership guard — anyone
  can edit).
- **Smoke:** create a study, redirected to detail, add an experiment
  with a ZFIN-picked fish, see it appear; edit a field, it persists.
- **Gate:** smoke green.

### Phase 6 — FE: Exposure + Observation forms (+ image upload)

- `/experiments/:id/exposures/new`, `/exposures/:id/edit` — chemical
  (manual for now, autocomplete-ready hook), concentration, route,
  vehicle, regimen, stages.
- `/exposures/:id/observations/new`, `/observations/:id/edit` —
  observation stage, phenotype items (frogpot picker), prevalence,
  severity, image drag-and-drop.
- **Smoke:** from an experiment, add an exposure and then an
  observation with an uploaded image; all appear on the study detail
  page.
- **Gate:** smoke green.

### Phase 7 — Release prep

- Delete `docs/plan-connect-form-to-api.md` and
  `docs/ui-rework-poc-spec.md` (replaced by this plan).
- Update `README.md` with dev quickstart (`just dev-api`, `just
  dev-client`, `just smoke`).
- Verify Docker build still green; Fly and GCP dry-run deploys clean.
- **Gate:** fresh clone → Docker build → deploy dry-run, all green.

---

## Test infrastructure

- **API** — pytest + `httpx.AsyncClient` + `respx` for external HTTP +
  in-memory SQLite. Already mostly in place.
- **UI smoke** — Playwright. One spec per FE phase under
  `client/tests/`. `playwright.config.ts` with `webServer` boots
  `just dev-api` + `just dev-client`. Headless in CI, headed locally
  via `just smoke:headed`.

## Justfile additions

- `just seed` — run the seed script.
- `just smoke`, `just smoke:headed` — Playwright.

## What's *not* in this pass

- Users, login, ORCID, per-user cabinet/tank, ownership / 403s.
- Schema changes. (If a gap forces one, we branch
  `../zebrafish-toxicology-atlas-schema` and switch to a local-path
  editable dep for that phase only.)
- NameRes chemical autocomplete (form field is ready for it; the call
  site lands when the endpoint does).
