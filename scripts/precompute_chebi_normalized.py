"""
precompute_chebi_normalized.py
-------------------------------
Two-phase precomputation pipeline for ChEBI chemical data.

Phase 1  Build synonym map
    Reads chebi_names.tsv.gz → {name: {CHEBI:xxx: ""}} → chebi_synonym_mapping.json

Phase 2  NodeNorm batch normalization
    Extracts every unique CHEBI ID from the synonym map, queries NodeNorm in
    batches, and saves results to chebi_normalized.json.
    Resumable: re-running skips IDs already present in the output file.

NOTE on images
    Structure images are NOT precomputed here.  ~370K PubChem API calls would
    take hours and produce tens of GB of PNGs.  Images are rendered on-demand
    by the /normalize-chemical server endpoint when the user explicitly
    requests them.

Usage
-----
    python precompute_chebi_normalized.py                   # full run
    python precompute_chebi_normalized.py --test-limit 300  # smoke test
    python precompute_chebi_normalized.py --skip-synonyms   # phase 2 only

Exit codes
----------
    0  completed (or nothing to do)
    1  input file not found
    2  network / API error
"""

import argparse
import csv
import gzip
import json
import sys
import time
from pathlib import Path

from normalize_chemical import _query_node_normalizer, _parse_node_norm

_REPO_ROOT          = Path(__file__).resolve().parents[1]
DEFAULT_CHEBI_NAMES = _REPO_ROOT / "zfin_test_data" / "chebi_names.tsv.gz"
DEFAULT_SYNONYM_MAP = _REPO_ROOT / "zfin_test_data" / "chebi_synonym_mapping.json"
DEFAULT_OUTPUT      = _REPO_ROOT / "zfin_test_data" / "chebi_normalized.json"

MAX_BATCH = 300


# ── Phase 1 ───────────────────────────────────────────────────────────────────

def build_synonym_map(path: Path) -> dict:
    """Read chebi_names.tsv.gz → {name: {CHEBI:xxx: "", ...}}."""
    synonyms: dict = {}
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            name  = row["name"].strip()
            curie = "CHEBI:{}".format(row["compound_id"].strip())
            if name not in synonyms:
                synonyms[name] = {}
            synonyms[name][curie] = ""
    return synonyms


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt(seconds: float) -> str:
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, s   = divmod(rem, 60)
    if h:
        return "{}h {}m {}s".format(h, m, s)
    if m:
        return "{}m {}s".format(m, s)
    return "{}s".format(s)


# ── CLI ───────────────────────────────────────────────────────────────────────

def build_parser():
    p = argparse.ArgumentParser(
        description="Precompute ChEBI synonym map and NodeNorm normalization data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--chebi-names",  default=str(DEFAULT_CHEBI_NAMES), metavar="PATH",
                   help="chebi_names.tsv.gz input (default: %(default)s)")
    p.add_argument("--synonym-map",  default=str(DEFAULT_SYNONYM_MAP), metavar="PATH",
                   help="chebi_synonym_mapping.json path (default: %(default)s)")
    p.add_argument("--output",       default=str(DEFAULT_OUTPUT),      metavar="PATH",
                   help="chebi_normalized.json output (default: %(default)s)")
    p.add_argument("--skip-synonyms", action="store_true",
                   help="Skip phase 1; use an existing chebi_synonym_mapping.json")
    p.add_argument("--batch-size", type=int, default=MAX_BATCH, metavar="N",
                   help="CURIEs per NodeNorm request, max {} (default: %(default)s)".format(MAX_BATCH))
    p.add_argument("--delay",      type=float, default=0.05, metavar="SEC",
                   help="Seconds between batches (default: %(default)s)")
    p.add_argument("--max-equiv",  type=int, default=20, metavar="N",
                   help="Max equivalent_identifiers stored per entry (default: %(default)s)")
    p.add_argument("--test-limit", type=int, default=None, metavar="N",
                   help="Only normalize the first N CHEBI IDs (smoke test)")
    return p


def main():
    args       = build_parser().parse_args()
    batch_size = max(1, min(args.batch_size, MAX_BATCH))
    synonym_map_path = Path(args.synonym_map)
    output_path      = Path(args.output)

    # ── Phase 1 ───────────────────────────────────────────────────────────────
    if not args.skip_synonyms:
        chebi_names_path = Path(args.chebi_names)
        if not chebi_names_path.exists():
            print("ERROR: {} not found".format(chebi_names_path), file=sys.stderr)
            sys.exit(1)
        print("Phase 1: building synonym map ...")
        t0       = time.time()
        synonyms = build_synonym_map(chebi_names_path)
        with open(synonym_map_path, "w", encoding="utf-8") as f:
            json.dump(synonyms, f, ensure_ascii=False)
        unique = {c for s in synonyms.values() for c in s}
        print("  {:,} name entries  |  {:,} unique CHEBI IDs  |  {}".format(
            len(synonyms), len(unique), _fmt(time.time() - t0)
        ))
        print("  Saved -> {}".format(synonym_map_path))
    else:
        if not synonym_map_path.exists():
            print("ERROR: synonym map not found: {}".format(synonym_map_path), file=sys.stderr)
            sys.exit(1)
        print("Phase 1: skipped (using {})".format(synonym_map_path))

    # ── Phase 2: collect IDs ──────────────────────────────────────────────────
    print("\nPhase 2: NodeNorm batch normalization")
    with open(synonym_map_path, encoding="utf-8") as f:
        synonyms = json.load(f)

    all_ids = sorted({curie for s in synonyms.values() for curie in s})
    print("  {:,} unique CHEBI IDs in synonym map".format(len(all_ids)))

    existing: dict = {}
    if output_path.exists():
        with open(output_path, encoding="utf-8") as f:
            existing = json.load(f)
        print("  Resuming: {:,} done, {:,} remaining".format(
            len(existing), len(all_ids) - len(existing)
        ))

    todo = [c for c in all_ids if c not in existing]

    if args.test_limit is not None:
        todo = todo[:args.test_limit]
        print("  TEST MODE: first {:,} IDs only".format(len(todo)))

    if not todo:
        print("  Nothing to do.")
        sys.exit(0)

    # ── Phase 2: batch loop ───────────────────────────────────────────────────
    results    = dict(existing)
    total      = len(todo)
    done       = 0
    errors     = 0
    t_start    = time.time()
    batches    = [todo[i : i + batch_size] for i in range(0, total, batch_size)]
    checkpoint_every = max(1, min(20, len(batches)))

    print("  {} batches of up to {}\n".format(len(batches), batch_size))

    for i, batch in enumerate(batches):
        try:
            raw = _query_node_normalizer(batch)
            for curie in batch:
                results[curie] = _parse_node_norm(curie, raw)
            done += len(batch)
        except Exception as e:
            print("  ERROR batch {}/{}: {}".format(i + 1, len(batches), e), file=sys.stderr)
            errors += len(batch)
            for curie in batch:
                if curie not in results:
                    results[curie] = {"normalized": False, "primary_id": None, "label": None,
                                      "description": None, "biolink_type": None,
                                      "equivalent_identifiers": []}

        processed = done + errors
        elapsed   = time.time() - t_start
        rate      = processed / elapsed if elapsed > 0 else 0
        eta       = (total - processed) / rate if rate > 0 else 0

        print("  [{:>6,}/{:<6,}]  {:5.1f}%  |  elapsed {}  |  ETA {}  |  {:.0f} IDs/s{}".format(
            processed, total,
            processed / total * 100,
            _fmt(elapsed), _fmt(eta), rate,
            "  [errors: {}]".format(errors) if errors else "",
        ))

        if (i + 1) % checkpoint_every == 0 or (i + 1) == len(batches):
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False)
            print("  >> checkpoint saved ({:,} entries)".format(len(results)))

        if args.delay > 0 and i < len(batches) - 1:
            time.sleep(args.delay)

    # ── Summary ───────────────────────────────────────────────────────────────
    norm_count = sum(1 for v in results.values() if v.get("normalized"))
    print("\nDone in {}.".format(_fmt(time.time() - t_start)))
    print("  {:,}/{:,} normalized  |  {:,} not found in NodeNorm".format(
        norm_count, len(results), len(results) - norm_count
    ))
    if errors:
        print("  {:,} network errors — re-run to retry".format(errors))
    print("  Output -> {}".format(output_path))
    sys.exit(0)


if __name__ == "__main__":
    main()
