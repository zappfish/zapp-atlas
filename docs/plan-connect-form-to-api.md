# Plan: Connect Form to FastAPI Backend

## Context

The frontend form (`ZappForm`) collects a `ZappObservation` and POSTs it as multipart FormData to `POST /observation` — a legacy Flask endpoint. The new FastAPI backend has `POST /studies` and `POST /studies/{id}/experiments` endpoints using LinkML-generated Pydantic models (`StudyCreate`, `ExperimentCreate`). These two data shapes don't match, and the `/observation` route isn't even proxied by Vite. The goal is to get the form submitting to the FastAPI backend as a functional MVP.

## Approach: Backend Translation Endpoint

Add a `POST /observations` endpoint on the FastAPI side that accepts the form's existing `ZappObservation` JSON shape, translates it to `StudyCreate`/`ExperimentCreate` models internally, and persists it. This avoids restructuring the form while keeping the translation logic server-side where it's easier to evolve with the schema.

## Data Model Mapping

### Fields that map cleanly

| Form field | API field |
|---|---|
| `provenance.annotator_orcid` | `StudyCreate.annotator` (formatted as `ORCID:xxxx-...`) |
| `provenance.source` (type+value) | `StudyCreate.publication` (e.g. `PMID:123` or `DOI:10.xxx`) |
| `rearing.standard` | `ExperimentCreate.standard_rearing_condition` |
| `rearing.non_standard_notes` | `ExperimentCreate.rearing_condition_comment` |
| `fish.strain_background` | `ExperimentCreate.fish` (lookup ZFIN ID from wild-type lines table) |
| `exposures[n].substance` | `StressorChemicalCreate.chemical_id` (ChemicalEntity) |
| `exposures[n].concentration` | `StressorChemicalCreate.concentration` (QuantityValue) |
| `exposures[n].route` | `ExposureEventCreate.route` |
| `exposures[n].type` | `RegimenCreate.exposure_regimen_type` |
| `exposures[n].start_stage/end_stage` | `ExposureEventCreate.exposure_start_stage/end_stage` |
| `exposures[n].repeated.*` | `RegimenCreate.*` fields |
| `phenotype.items[n]` | `PhenotypeCreate` inside `PhenotypeObservationSetCreate` |
| `phenotype.observation_stage` | `PhenotypeCreate.stage` |

### Fields without a mapping for MVP

These are dropped or stored in comment fields where possible:

- `provenance.annotator_name` — no API field; drop for now
- `image` — no file upload in FastAPI yet; skip for MVP
- `exposures[n].pattern` (static/static_renewal/flow_through) — store as `additional_exposure_condition`

### Structural mismatch: phenotypes

In the LinkML model, phenotypes live *inside* exposure events (via `phenotype_observation`). The form has a single global phenotype section. For MVP, we'll attach the phenotype observation set to the **first** exposure event.

## Implementation Steps

### 1. New backend router: `server/api/routers/observations.py` (new file)

- `POST /observations` endpoint accepting JSON body matching the form's `ZappObservation` shape
- Define a Pydantic model mirroring `ZappObservation` for request validation
- Translation function that maps form data → `StudyCreate` with one inline `ExperimentCreate`
- Calls existing `create_study()` service to persist
- Returns the created study ID

### 2. Wire router into app: `server/api/main.py`

- Import and include the new `observations_router`

### 3. Update Vite proxy: `client/vite.config.js`

- Add `/observations` to the proxy config so dev server forwards to the API

### 4. Update form submission: `client/src/components/ZappForm/index.tsx`

- Change `handleSubmit` to POST JSON to `/observations` instead of multipart FormData to `/observation`
- Remove username/password fields (no auth for MVP)
- Send the `data` object as JSON directly
- Handle the response (show created study ID on success)

### 5. Carry fish ZFIN data through the form

- Currently the form stores `strain_background` as a display code (e.g. "AB"), but the API needs `zfin_id` (e.g. `ZFIN:ZDB-FISH-150901-27842`) and `name`
- Update `FishInfoSection.tsx` to also store `fishId` from the selected wild-type line in the form state
- Add optional `zfin_fish_id` field to the fish section of the Zod schema (`client/src/schema.ts`)

## Files to modify

| File | Change |
|---|---|
| `server/api/routers/observations.py` | **New file** — translation endpoint |
| `server/api/main.py` | Add observations router |
| `client/vite.config.js` | Add `/observations` proxy route |
| `client/src/components/ZappForm/index.tsx` | Update submission to POST JSON, remove auth fields |
| `client/src/components/ZappForm/FishInfoSection.tsx` | Store ZFIN IDs on selection |
| `client/src/schema.ts` | Add optional `zfin_fish_id` field |

## Verification

1. Run `just dev-api` and `just dev-client`
2. Fill out the form with sample data (pick a wild-type line, add an exposure, select a phenotype)
3. Submit and verify a 201 response with a study ID
4. `GET /studies/{id}` to confirm the data was persisted correctly
5. Run existing tests: `just test` to confirm nothing broke
