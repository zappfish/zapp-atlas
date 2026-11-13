# Fish picker prototype

The working prototype of the fish description widget from the fish data-model
work (PR #154), handed off as-is — Aaron is off the project. It is a **spec
that runs**, not production code: per #152 the real widget is a React build
inside the signed-in app, but everything this page does — what the curator is
asked, what attaches silently, and the exact `FishCreate` payload it emits —
is the behavior that build should reproduce.

## Run it

```sh
git clone -b fish-picker-handoff https://github.com/zappfish/zapp-atlas.git
cd zapp-atlas
just install        # uv + npm deps (npm half isn't needed for this, but is cheap)
just fetch-zfin     # one-time, ~77 MB of ZFIN bulk files into the gitignored data dir
just fish-picker    # starts the API on :8000 with dev CORS, prints this page's path
```

Then open `prototypes/fish_picker/index.html` in a browser (plain `file://` is
fine — that's what the dev CORS flag is for). The pill in the page header must
read **“live ZFIN index”**; if it doesn't, the API isn't up and the page is on
its tiny embedded fallback (3 alleles, 3 backgrounds), which exists so the file
also opens standalone as a design reference.

Good inputs to try: `fh111`, `ti282a` (point mutants), `mpeg1:YFP` (construct
fragment → transgenic), `fgf8a` (search by gene), plus a background from the
picklist. The right-hand pane shows the exact payload the API accepts and a
log narrating which ZFIN ids attached and why.

## What it demonstrates

- Typed search over all ~81k ZFIN alleles (symbol / gene / construct), ranked
  exact > prefix > substring — one search box, no type filters.
- Picking a hit fills the card: CURIE ids, alteration type, affected gene,
  constructs, registering institution. The curator answers only zygosity
  (fish + optional mother/father).
- Background picklist (32 wild-type lines); a wildtype-only fish silently gets
  **both** its genotype and fish ids.
- The morphant rule: with injected reagents a fish keeps the strain's GENO id
  but **not** its FISH id — an injected fish is a different ZFIN record.
- “Unknown background” is stored as absence, never a placeholder.
- `V2_REAGENTS` (a const near the top of the script) unhides the injected-
  reagents section — modeled and served (`/api/zfin/reagents`) but deliberately
  not surfaced in v1.

## What it is not

- Not production code, and not the production rendering path: #152 puts the
  widget in React behind login, with display strings computed **server-side**.
  The genotype-string preview and the mutagen gloss in this page's JS are
  prototype conveniences that must move into the API when the real widget is
  built (they were slated for the resolver PR).
- `ZAPP_CORS_DEV` is a GET-only, local-dev-only flag. It must stay off in any
  deployment.

## Where the fish work stands

- **PR #154** carries the model (flat Fish, mapped ids, transient reagents,
  tank nicknames), the ZFIN lookup pipeline, the legacy-DB migration, and the
  QC notebook — its description is the summary. The notebook
  (`notebooks/zfin_ingest_qc.ipynb`, committed executed; `just qc-report`
  renders it) is the provenance record: corpus evidence for every enum and
  identity decision, asserted against the production index.
- **Deferred, in order of likely need:** the resolver
  (description → 0-or-1 ZFIN record, plus its inverse for hydrating a saved
  fish — its input files are already in `fetch-zfin` and the identity rules
  are pinned and asserted in the notebook); server-side display strings per
  #152; surfacing reagents (v2); the chemical half of #113.
- ARCHITECTURE.md's “Reference data” section (on this branch) documents the
  fetch → index → search-endpoints → QC-notebook pattern.

## Branch mechanics

This branch is `fish-genotype-zfin-ids` (PR #154, base `2e4e02a`) plus one
commit adding this directory and the `fish-picker` recipe. It is a frozen,
self-contained snapshot: clone-and-run works regardless of what happens to
#154. Main has moved ~200 commits since the base and #154 currently conflicts
with it — reconciling is a separate task; when the #154 content lands
somewhere, cherry-pick this branch's tip commit onto it.
