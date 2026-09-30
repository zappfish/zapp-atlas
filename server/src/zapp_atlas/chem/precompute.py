"""Precompute the ChEBI inputs for ``build_cache``: a synonym map and NodeNorm results.

Phase 1 reads ChEBI's ``names.tsv.gz`` flat file (``compound_id`` and ``name``
columns) into ``{name: {CHEBI:xxx: ""}}`` and writes ``chebi_synonym_mapping.json``.

Phase 2 normalizes every ChEBI ID in that map through NodeNorm in batches and
writes ``chebi_normalized.json``. It checkpoints as it goes, and re-running
skips IDs already in the output, so an interrupted run can be resumed.

    uv run python -m zapp_atlas.chem.precompute
    uv run python -m zapp_atlas.chem.precompute --test-limit 300   # smoke test
    uv run python -m zapp_atlas.chem.precompute --skip-synonyms    # phase 2 only
"""

import argparse
import csv
import gzip
import json
import sys
import time
from pathlib import Path

import httpx

from zapp_atlas.chem.normalize import parse_node_norm, query_node_normalizer
from zapp_atlas.settings import DEFAULT_DATA_DIR

DEFAULT_INPUT_DIR = DEFAULT_DATA_DIR / "chebi"
MAX_BATCH = 300


def build_synonym_map(path: Path) -> dict[str, dict[str, str]]:
    synonyms: dict[str, dict[str, str]] = {}
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            curie = f"CHEBI:{row['compound_id'].strip()}"
            synonyms.setdefault(row["name"].strip(), {})[curie] = ""
    return synonyms


def _fmt(seconds: float) -> str:
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m {s}s" if h else f"{m}m {s}s" if m else f"{s}s"


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def normalize_all(
    ids: list[str], existing: dict, output: Path, batch_size: int, delay: float
) -> tuple[dict, int]:
    """Normalize ``ids`` in batches, checkpointing into ``output``; return (results, errors)."""
    results = dict(existing)
    batches = [ids[i : i + batch_size] for i in range(0, len(ids), batch_size)]
    checkpoint_every = max(1, min(20, len(batches)))
    processed = errors = 0
    t_start = time.time()
    print(f"  {len(batches)} batches of up to {batch_size}\n")

    for i, batch in enumerate(batches):
        try:
            raw = query_node_normalizer(batch)
            for curie in batch:
                results[curie] = parse_node_norm(curie, raw)
        except httpx.HTTPError as e:
            # Left out of the output rather than recorded as unnormalized, so
            # that the next run picks them up again.
            print(f"  ERROR batch {i + 1}/{len(batches)}: {e}", file=sys.stderr)
            errors += len(batch)
        processed += len(batch)

        elapsed = time.time() - t_start
        rate = processed / elapsed if elapsed > 0 else 0
        eta = (len(ids) - processed) / rate if rate > 0 else 0
        print(
            f"  [{processed:>6,}/{len(ids):<6,}]  {processed / len(ids) * 100:5.1f}%  |  "
            f"elapsed {_fmt(elapsed)}  |  ETA {_fmt(eta)}  |  {rate:.0f} IDs/s"
            + (f"  [errors: {errors}]" if errors else "")
        )

        if (i + 1) % checkpoint_every == 0 or i + 1 == len(batches):
            _write_json(output, results)
            print(f"  >> checkpoint saved ({len(results):,} entries)")

        if delay > 0 and i < len(batches) - 1:
            time.sleep(delay)

    return results, errors


def main() -> int:
    p = argparse.ArgumentParser(
        description="Precompute the ChEBI synonym map and NodeNorm normalization data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--chebi-names", type=Path, default=DEFAULT_INPUT_DIR / "names.tsv.gz")
    p.add_argument(
        "--synonym-map", type=Path, default=DEFAULT_INPUT_DIR / "chebi_synonym_mapping.json"
    )
    p.add_argument("--output", type=Path, default=DEFAULT_INPUT_DIR / "chebi_normalized.json")
    p.add_argument(
        "--skip-synonyms",
        action="store_true",
        help="Skip phase 1; use an existing synonym map",
    )
    p.add_argument("--batch-size", type=int, default=MAX_BATCH, help=f"max {MAX_BATCH}")
    p.add_argument("--delay", type=float, default=0.05, help="Seconds between batches")
    p.add_argument("--test-limit", type=int, default=None, help="Only normalize the first N IDs")
    args = p.parse_args()

    if not args.skip_synonyms:
        if not args.chebi_names.exists():
            print(f"ERROR: {args.chebi_names} not found", file=sys.stderr)
            return 1
        print("Phase 1: building synonym map ...")
        t0 = time.time()
        synonyms = build_synonym_map(args.chebi_names)
        _write_json(args.synonym_map, synonyms)
        unique = {c for s in synonyms.values() for c in s}
        print(
            f"  {len(synonyms):,} names  |  {len(unique):,} unique CHEBI IDs  |  "
            f"{_fmt(time.time() - t0)}\n  Saved -> {args.synonym_map}"
        )
    elif not args.synonym_map.exists():
        print(f"ERROR: synonym map not found: {args.synonym_map}", file=sys.stderr)
        return 1

    print("\nPhase 2: NodeNorm batch normalization")
    with args.synonym_map.open(encoding="utf-8") as f:
        synonyms = json.load(f)
    all_ids = sorted({curie for s in synonyms.values() for curie in s})

    existing: dict = {}
    if args.output.exists():
        with args.output.open(encoding="utf-8") as f:
            existing = json.load(f)
        print(f"  Resuming: {len(existing):,} done, {len(all_ids) - len(existing):,} remaining")

    todo = [c for c in all_ids if c not in existing]
    if args.test_limit is not None:
        todo = todo[: args.test_limit]
    if not todo:
        print("  Nothing to do.")
        return 0

    batch_size = max(1, min(args.batch_size, MAX_BATCH))
    results, errors = normalize_all(todo, existing, args.output, batch_size, args.delay)

    normalized = sum(1 for v in results.values() if v.get("normalized"))
    print(f"\n  {normalized:,}/{len(results):,} normalized  |  Output -> {args.output}")
    if errors:
        print(f"  {errors:,} network errors — re-run to retry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
