# extdata

Read-only reference data the app ships: ontology files built offline from
pinned upstream releases. Nothing here is built at runtime, and none of it
lives on the app's persistent volume.

```sh
just extdata        # build dist/ (needs docker and uv)
```

The first build downloads the ROBOT image and the sources, and takes a few
minutes. The app finds the bundle at `extdata/dist`
(`ZAPP_EXTDATA_DIR` overrides that); without it, `/extdata` answers 404 and
nothing else is affected.

## What is in the bundle

| File | From | Used by |
|---|---|---|
| `zp.json`, `zp.json.gz` | ZP's ZAPP subset | client: phenotype picker |
| `zfa.json`, `zfa.json.gz` | ZFA | client: phenotype picker (anatomy) |
| `zfin_counts.tsv` | ZP's `fish_to_phenotype.tsv` | client: sorting by ZFIN usage |
| `labels.db` | ZP, ZFA (same filtered OWL as the JSON), ChEBI lite | server: label lookups |
| `manifest.json` | | everything: versions, sizes, checksums |

An ontology's JSON and its rows in `labels.db` come from one filtered OWL
file, so the client and server always agree on which terms exist. Filtering
keeps only what the phenotype picker reads: labels, definitions, synonyms,
and the relationships its hierarchies are built from (`is_a`, plus `part_of` for ZFA
and `UPHENO:0000003` for ZP). Obsolete terms and logical axioms are dropped.

Two ZP-specific steps:

- **ZAPP preferred labels.** A term's label is replaced by its ZAPP preferred
  label (the exact synonym annotated `OMO:0002001` -> ZAPP); the original
  label is kept as a synonym. See `sparql/zapp-preferred-label.ru`.
- **ZFIN counts** are the number of curated rows per ZP term in
  `fish_to_phenotype.tsv`, with no rollup to ancestors. They live in their own
  file rather than in the ontology.

`labels.db` is a single `term (id, label)` table keyed by CURIE; the server
reads it through `zapp_atlas/labels.py`. Terms without a label are left out
(including ChEBI's obsolete terms, which have none), and callers fall back to
the CURIE.

## Temporary workarounds

All three are upstream ZP bugs. The first two have workarounds, marked
`TEMPORARY` where they live; remove them once a ZP release fixes them.

- The ZAPP subset is missing its `UPHENO:0000003` edges, so the build adds
  them with the uPheno ROBOT plugin (`UPHENO_PLUGIN_URL` in `sources.mk`, and
  the first step of the `zp.owl` rule in the `Makefile`).
- Some ZP terms carry two ZAPP preferred labels; the alphabetically first wins.
- Many ZP terms carry two definitions; the OBO JSON keeps one of them. There
  is no workaround for this.

## Versioning

Every input is pinned in `sources.mk` (and the ROBOT image in the `Makefile`).
Never point one at a "latest" URL: the bundle is named by a hash of the files
that define it (`./hash.sh`), so an input that changed behind a stable URL
would change the data without changing its name.

To update a source, change its pin and rebuild. The hash changes with it.

## Deployment

The bundle is copied into the app's Docker image from `extdata/dist`, so the
deploy workflows put it there before `flyctl deploy` (`ci.sh fetch`):

- If a GitHub release `extdata-<hash>` exists, it is downloaded.
- Otherwise the bundle is built in the job. Previews cache it by hash, so
  later pushes to the same PR don't rebuild it.

Only production deploys publish (`ci.sh publish`): when an app release
deploys with a bundle no release holds yet, it is published as
`extdata-<hash>`. A PR that doesn't touch the files above finds its hash
already published and downloads it; one that does builds its own and
publishes nothing. These releases are never marked "Latest", and the deploy
workflow ignores them.
