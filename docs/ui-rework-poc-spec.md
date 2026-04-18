# ZAPP Atlas UI Rework — Pre-Alpha POC Spec

## Overview

Rework the current single-page observation form into a multi-page CRUD
application with navigation, fake user sessions, and incremental data entry.
The goal is a proof of concept that a frontend developer can later refine.

---

## 1. Fake User System

No real authentication. A persistent menu (header dropdown) lets the visitor
switch between five hard-coded personas. Selection is stored in React context
and sent to the API as a header or query param so the server can enforce
ownership.

### Personas

| Name | ORCID | Lab (ZFIN) | Pre-loaded data |
|---|---|---|---|
| Dr. A. Bisphenol | ORCID:0000-0001-0101-0101 | ZFIN:ZDB-LAB-000001-AA | 3 chemicals in cabinet, 2 fish in tank, 1 study with 2 experiments |
| Dr. Sonic H. Hog | ORCID:0000-0002-0202-0202 | ZFIN:ZDB-LAB-000002-BB | 2 chemicals, 3 fish, 1 study with 1 experiment |
| Dr. Retinoic Acid | ORCID:0000-0003-0303-0303 | ZFIN:ZDB-LAB-000003-CC | 1 chemical, 1 fish, no studies |
| Dr. Wnt Signalpez | ORCID:0000-0004-0404-0404 | ZFIN:ZDB-LAB-000004-DD | empty cabinet & tank, no studies |
| Dr. Danio Frankfish | ORCID:0000-0005-0505-0505 | ZFIN:ZDB-LAB-000005-EE | empty cabinet & tank, no studies |

The User entity will be added to the LinkML schema (branch of sibling repo)
with fields: `id`, `name`, `orcid`, `lab`, plus multivalued relationships
`chemical_cabinet → ChemicalEntity` and `fish_tank → Fish`.

A `created_by` foreign key will be added to `Study` pointing to `User`, and
a `uv` branch dependency on the schema repo will be used until merged.

### Schema Changes Required

In the `zebrafish-toxicology-atlas-schema` sibling repo (new branch):

- Add `User` class with slots: `id` (int PK), `name`, `orcid` (uriorcurie,
  ORCID pattern), `lab` (uriorcurie, ZFIN pattern)
- Add `chemical_cabinet` slot: multivalued, range ChemicalEntity
- Add `fish_tank` slot: multivalued, range Fish
- Add `created_by` slot on Study: range User (foreign key)
- Regenerate SQLAlchemy + Pydantic models

---

## 2. Navigation & Routing

### Public (no login required)

| Route | Page | Description |
|---|---|---|
| `/` | Study List | Paginated list of all studies. Home page. |
| `/studies/:id` | Study Detail | Read-only view of study + experiments + exposures + observations + images |
| `/experiments/:id` | Experiment Detail | Read-only view of a single experiment (deep-linked from study) |

### Logged-in only

| Route | Page | Description |
|---|---|---|
| `/cabinet` | Chemical Cabinet | User's bookmarked chemicals. Add/remove. |
| `/tank` | Fish Tank | User's bookmarked fish. Add/remove with ZFIN autocomplete. |
| `/studies/new` | Create Study | Small form: publication, lab & annotator auto-filled from user. |
| `/studies/:id/edit` | Edit Study | Same form, pre-populated. Owner only. |
| `/studies/:id/experiments/new` | Create Experiment | Fish (from tank or manual), rearing conditions, controls. |
| `/experiments/:id/edit` | Edit Experiment | Same form, pre-populated. Owner only. |
| `/experiments/:id/exposures/new` | Add Exposure Event | Chemical, concentration, route, duration, regimen, stages. |
| `/exposures/:id/edit` | Edit Exposure Event | Same form, pre-populated. Owner only. |
| `/exposures/:id/observations/new` | Add Observation | Phenotype picker, prevalence, severity, image upload. |
| `/observations/:id/edit` | Edit Observation | Same form, pre-populated. Owner only. |

Header shows: nav links (Home), user dropdown (switch user or "Browse as
guest"), and when logged in: links to Cabinet, Tank.

---

## 3. Pages

### 3.1 Study List (Home — `/`)

- Simple paginated table/list
- Columns: publication, lab, annotator(s), number of experiments
- Click row → study detail
- When logged in, "New Study" button visible
- Pagination controls (prev/next, using existing `limit`/`offset` API params)

### 3.2 Study Detail (`/studies/:id`)

Read-only (public). Shows:

- **Study metadata**: publication, lab, annotator ORCIDs, created-by user
- **Experiments list**: for each experiment:
  - Fish (ZFIN ID + name)
  - Rearing conditions (standard? + comment)
  - Controls (type, vehicle, comment)
  - Exposure events, each showing:
    - Chemical(s) with concentration
    - Route, duration, regimen type & details
    - Start/end stages
    - Phenotype observations: term, severity, prevalence, images

If current user is the owner: "Edit Study" button, "Add Experiment" button,
edit/add buttons on nested items.

### 3.3 Create / Edit Study (`/studies/new`, `/studies/:id/edit`)

Small form (reused for both create and edit):

- **Publication** — text input (PMID, DOI, or free text)
- **Lab** — auto-filled from logged-in user, editable
- **Annotator(s)** — auto-filled from logged-in user's ORCID, can add more

On submit → create: POST to API, redirect to study detail page.
On submit → edit: PATCH to API, redirect to study detail page.

### 3.4 Create / Edit Experiment (`/studies/:id/experiments/new`, `/experiments/:id/edit`)

Form fields:

- **Fish** — autocomplete powered by user's fish tank entries + ZFIN search
  fallback. Selecting from tank = instant. Typing triggers ZFIN autocomplete
  (`https://zfin.org/action/quicksearch/autocomplete?category=Fish&q=...`).
  Selected fish is validated and stored in Fish table (get-or-create).
- **Standard rearing condition** — boolean toggle
- **Rearing condition comment** — text, shown when not standard
- **Controls** — repeatable section:
  - Control type (text)
  - Vehicle if treated (enum)
  - Comment

On submit → redirects to experiment detail or back to parent study.

### 3.5 Add / Edit Exposure Event (`/experiments/:id/exposures/new`, `/exposures/:id/edit`)

Form fields:

- **Chemical(s)** — repeatable. Pick from cabinet or enter manually
  (name + identifier type + ID). Chemical validated & stored (get-or-create).
  - Concentration: numeric value + unit (uM, mg/L, custom)
  - Manufacturer (optional)
- **Route of exposure** — enum (water, injected, ingested, gavage)
- **Vehicle** — enum
- **Exposure type** — continuous or repeated
- **Start stage** — value + unit (hpf, dpf, month)
- **End stage** — value + unit
- **Regimen details** (if repeated):
  - Number of individual exposures
  - Duration per exposure + unit
  - Interval between exposures + unit
  - Total exposure duration + unit

### 3.6 Add / Edit Observation (`/exposures/:id/observations/new`, `/observations/:id/edit`)

Form fields:

- **Observation stage** — value + unit
- **Phenotype items** — repeatable:
  - Phenotype term — use existing ontology picker modal (ZFA → ZP)
  - Prevalence — percentage (0–100)
  - Severity — mild / moderate / severe
- **Image upload** — drag-and-drop or file picker
  - Magnification, resolution, scale bar (optional metadata)
- **Control images** — optional, with phenotype ID reference

### 3.7 Chemical Cabinet (`/cabinet`)

- Table listing user's saved chemicals: name, ChEBI ID, CAS ID
- "Add Chemical" — basic form: name, identifier type (ChEBI/CAS), ID value.
  (Nice autocomplete coming via separate NameRes PR.)
- "Remove" button per row
- No link to studies/experiments — just the shortcut list

### 3.8 Fish Tank (`/tank`)

- Table listing user's saved fish: ZFIN ID, name
- "Add Fish" — autocomplete input powered by ZFIN:
  `GET https://zfin.org/action/quicksearch/autocomplete?category=Fish&q={input}`
  Returns `{ id, name, value, url, category }`. We store `ZFIN:{id}` as
  the Fish primary key and `name` as the name.
- "Remove" button per row

---

## 4. API Changes

### New / Modified Endpoints

```
# Users (fake, pre-seeded)
GET    /users                  — list all fake users
GET    /users/:id              — get user with cabinet & tank

# Chemical Cabinet
GET    /users/:id/cabinet      — list chemicals in user's cabinet
POST   /users/:id/cabinet      — add chemical to cabinet { chemical_name, chebi_id?, cas_id? }
DELETE /users/:id/cabinet/:uri — remove chemical from cabinet

# Fish Tank
GET    /users/:id/tank         — list fish in user's tank
POST   /users/:id/tank         — add fish to tank { zfin_id, name }
DELETE /users/:id/tank/:zfin_id — remove fish from tank

# ZFIN proxy (avoid CORS from client)
GET    /zfin/fish-autocomplete?q=  — proxies to zfin.org autocomplete, returns results

# Exposure Events (new)
POST   /experiments/:id/exposures  — create exposure event for experiment
GET    /exposures/:id              — get single exposure event
PATCH  /exposures/:id              — update exposure event

# Observations (new)
POST   /exposures/:id/observations — create observation set for exposure
GET    /observations/:id           — get single observation set
PATCH  /observations/:id           — update observation set

# Images
POST   /images/upload              — upload image, returns key/URL
GET    /images/:key                — retrieve image (or redirect to Tigris URL)

# Existing (modified)
POST   /studies                    — now requires user ID, sets created_by
PATCH  /studies/:id                — now supports nested experiment updates?
                                     Or keep shallow — TBD based on schema
GET    /studies/:id                — include created_by user info in response
```

### Ownership Enforcement

- Mutation endpoints (POST, PATCH, DELETE) check that the requesting user
  matches `created_by` on the study. If not, return 403.
- The "current user" is passed via `X-User-Id` header (no real auth).

### Drop Legacy Flask

- Remove the Flask `POST /observation` endpoint and associated code
- All functionality moves to FastAPI

---

## 5. Image Storage

### Architecture

Thin `Storage` abstraction with two backends:

- **Production (Fly.io):** Tigris object storage (S3-compatible via boto3)
  - Bucket created via `fly storage create`
  - Env vars auto-set: `AWS_ENDPOINT_URL_S3`, `AWS_ACCESS_KEY_ID`,
    `AWS_SECRET_ACCESS_KEY`, `BUCKET_NAME`
- **Local development:** filesystem fallback at `server/data/uploads/`
  - Used when `AWS_ENDPOINT_URL_S3` is not set

### Storage Abstraction

```python
class Storage:
    """S3/Tigris in production, local filesystem in development."""

    def put(self, key: str, data: bytes, content_type: str) -> str: ...
    def get(self, key: str) -> bytes: ...
    def get_url(self, key: str) -> str: ...
    def delete(self, key: str) -> None: ...
```

Images stored with keys like `images/{study_id}/{experiment_id}/{uuid}.{ext}`.

### Fly.io Setup Required

```bash
fly storage create --app zapp-atlas
# sets BUCKET_NAME, AWS_ENDPOINT_URL_S3, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
```

Add `boto3` to Python dependencies.

---

## 6. Pre-loaded Seed Data

On first startup (or via a seed script), populate:

### Dr. A. Bisphenol's data

**Cabinet:** Bisphenol A (CHEBI:33216), Bisphenol S (CHEBI:34372),
17β-Estradiol (CHEBI:16469)

**Tank:** AB (ZFIN:ZDB-FISH-150901-27842), Casper (ZFIN:ZDB-FISH-150901-29085)

**Study:** BPA developmental toxicity study
- Publication: "PMID:12345678"
- Experiment 1: AB fish, standard rearing, water exposure to BPA 10 uM,
  continuous, 6-72 hpf, observation: pericardial edema (moderate, 60%)
- Experiment 2: AB fish, standard rearing, water exposure to BPA 50 uM,
  continuous, 6-72 hpf, observation: spinal curvature (severe, 85%)

### Dr. Sonic H. Hog's data

**Cabinet:** Cyclopamine (CHEBI:4023), DMSO (CHEBI:28262)

**Tank:** TU (ZFIN:ZDB-FISH-150901-27843), AB (shared),
TL (ZFIN:ZDB-FISH-150901-27844)

**Study:** Hedgehog pathway chemical screen
- Publication: "DOI:10.1234/fake.2024.001"
- Experiment 1: TU fish, standard rearing, water exposure to cyclopamine 5 uM,
  continuous, 10-48 hpf, observation: cyclopia (severe, 90%)

### Dr. Retinoic Acid's data

**Cabinet:** all-trans-Retinoic acid (CHEBI:15367)

**Tank:** AB (shared)

No studies yet.

### Dr. Wnt Signalpez & Dr. Danio Frankfish

Empty cabinets, empty tanks, no studies. Fresh accounts for testing creation
flows.

---

## 7. Frontend Architecture

### Stack

- React 18 + TypeScript (existing)
- React Router for page routing (add)
- React Context for fake user session state
- Zod for form validation (existing)
- Existing `client/src/ui/` components reused
- Frogpot for phenotype ontology picker (existing)
- Keep it simple — no heavy state management, no component library

### Key Components

```
App
├── Header (nav links, user switcher dropdown)
├── Routes
│   ├── StudyListPage
│   ├── StudyDetailPage
│   ├── StudyFormPage (create/edit)
│   ├── ExperimentDetailPage
│   ├── ExperimentFormPage (create/edit)
│   ├── ExposureFormPage (create/edit)
│   ├── ObservationFormPage (create/edit)
│   ├── CabinetPage
│   └── TankPage
└── UserContext (provides current user to all components)
```

### User Context

```tsx
interface FakeUser {
  id: number;
  name: string;
  orcid: string;
  lab: string;
}

const UserContext = React.createContext<{
  user: FakeUser | null;       // null = browsing as guest
  setUser: (u: FakeUser | null) => void;
}>();
```

---

## 8. Implementation Order

1. **Schema changes** — branch the schema repo, add User class + relationships,
   regenerate models, set up uv branch dependency
2. **API: User, cabinet, tank endpoints** — seed fake users, cabinet/tank CRUD
3. **API: ZFIN proxy** — fish autocomplete proxy endpoint
4. **API: Exposure & observation CRUD** — fill in missing endpoints
5. **API: Image storage** — Storage abstraction + upload/retrieve endpoints
6. **API: Ownership enforcement** — X-User-Id header, created_by on Study, 403s
7. **API: Drop legacy Flask** — remove Flask app, observation endpoint, credentials
8. **Frontend: Routing & layout** — React Router, Header, UserContext
9. **Frontend: Study list & detail pages** — public read-only views
10. **Frontend: Study/experiment/exposure/observation forms** — create & edit
11. **Frontend: Cabinet & tank pages** — with ZFIN autocomplete for tank
12. **Frontend: Image upload** — in observation form
13. **Seed data script** — populate fake users + their pre-loaded data
14. **Fly.io setup** — Tigris bucket for image storage
