"""
Build a SQLite cache of ChEBI chemical data from local files, then append
supplemental rows for the small set of non-CHEBI vehicle meanings
(PBS, Albumin/BSA, Solketal, …) by querying NodeNorm + PubChem.

Sources (all local):
  - chebi_normalized.json      — precomputed NodeNorm results keyed by CHEBI ID
  - chebi_synonym_mapping.json — synonym name -> {CHEBI:xxx: ...} mappings
  - chebi.obo                  — ChEBI ontology file (SMILES extraction only)

Vehicle overrides (requires internet):
  - NodeNorm for label + equivalent identifiers
  - PubChem PUG-REST for SMILES + description (PUBCHEM.COMPOUND IDs only)

Run:
    python scripts/build_chebi_and_vehicle_cache.py
    python scripts/build_chebi_and_vehicle_cache.py --resume --test-limit 1000
    python scripts/build_chebi_and_vehicle_cache.py --skip-vehicles   # offline, skip NodeNorm step
"""

import argparse
import json
import re
import sqlite3
import time
from pathlib import Path

import sys

# normalize_chemical lives in the same scripts/ directory
_SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS_DIR))
from normalize_chemical import normalize_curie, find_visualizable_curie, visualize_chemical

_HTML_TAG = re.compile(r'<[^>]+>')

_REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NORMALIZED = _REPO_ROOT / "zfin_test_data" / "chebi_normalized.json"
DEFAULT_SYNONYMS = _REPO_ROOT / "zfin_test_data" / "chebi_synonym_mapping.json"
DEFAULT_OBO = _REPO_ROOT / "zfin_test_data" / "chebi.obo"
DEFAULT_OUTPUT = _REPO_ROOT / "zfin_test_data" / "chebi_and_vehicle_cache.db"

# Non-CHEBI vehicle meanings — update when VehicleEnum gains new non-CHEBI entries
VEHICLE_OVERRIDE_MEANINGS = [
    "PUBCHEM.COMPOUND:24978514",  # Phosphate-buffered saline (PBS)
    "UMLS:C0036774",              # Bovine serum albumin (BSA)
    "UNII:3XK098O8ZW",            # Solketal
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS chemicals (
    chebi_id    TEXT PRIMARY KEY,
    primary_id  TEXT,
    label       TEXT,
    description TEXT,
    equiv_ids   TEXT,
    smiles      TEXT
);
CREATE INDEX IF NOT EXISTS idx_primary_id ON chemicals(primary_id);

CREATE TABLE IF NOT EXISTS synonyms (
    synonym_lower TEXT NOT NULL,
    orig_name     TEXT NOT NULL,
    chebi_id      TEXT NOT NULL,
    PRIMARY KEY (synonym_lower, chebi_id)
);
CREATE INDEX IF NOT EXISTS idx_syn_lower ON synonyms(synonym_lower);
"""


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _fmt(seconds: float) -> str:
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    m, s = divmod(seconds, 60)
    if m < 60:
        return f"{m}m{s:02d}s"
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m{s:02d}s"


# ---------------------------------------------------------------------------
# ChEBI sections (local files)
# ---------------------------------------------------------------------------

def parse_obo_smiles(obo_path: Path) -> dict[str, str]:
    """Stream chebi.obo and extract CHEBI_ID -> SMILES mappings."""
    print(f"[OBO] Parsing SMILES from {obo_path} ...")
    smiles_map: dict[str, str] = {}
    current_id: str | None = None
    t0 = time.monotonic()
    lines_read = 0

    with open(obo_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            lines_read += 1
            line = line.rstrip("\n")
            if line == "[Term]":
                current_id = None
                continue
            if line.startswith("id: CHEBI:"):
                current_id = line[4:].strip()
                continue
            if current_id and line.startswith('property_value: chemrof:smiles_string "'):
                rest = line[len('property_value: chemrof:smiles_string "'):]
                end = rest.find('"')
                if end != -1:
                    smiles_map[current_id] = rest[:end]

    elapsed = time.monotonic() - t0
    print(f"[OBO] Done — {len(smiles_map):,} SMILES in {lines_read:,} lines ({_fmt(elapsed)})")
    return smiles_map


def build_chemicals(conn: sqlite3.Connection,
                    normalized_path: Path,
                    smiles_map: dict[str, str],
                    batch_size: int = 500,
                    resume: bool = False,
                    test_limit: int | None = None) -> None:

    print(f"[chemicals] Loading {normalized_path} ...")
    with open(normalized_path, encoding="utf-8") as f:
        normalized: dict = json.load(f)

    entries = list(normalized.items())
    if test_limit is not None:
        entries = entries[:test_limit]
    total = len(entries)
    print(f"[chemicals] {total:,} entries to process")

    existing: set[str] = set()
    if resume:
        existing = {row[0] for row in conn.execute("SELECT chebi_id FROM chemicals")}
        print(f"[chemicals] Resume mode: {len(existing):,} already in DB, skipping")

    done = 0
    skipped = 0
    t0 = time.monotonic()
    batch: list[tuple] = []

    for chebi_id, result in entries:
        if chebi_id in existing:
            skipped += 1
            continue

        primary_id = result.get("primary_id")
        label = result.get("label")
        description = result.get("description")
        equiv_ids = json.dumps(result.get("equivalent_identifiers") or [])
        smiles = smiles_map.get(chebi_id)

        batch.append((chebi_id, primary_id, label, description, equiv_ids, smiles))

        if len(batch) >= batch_size:
            conn.executemany(
                "INSERT OR REPLACE INTO chemicals "
                "(chebi_id, primary_id, label, description, equiv_ids, smiles) "
                "VALUES (?,?,?,?,?,?)",
                batch,
            )
            conn.commit()
            done += len(batch)
            batch = []

            elapsed = time.monotonic() - t0
            pct = 100 * done / max(total - skipped, 1)
            rate = done / elapsed if elapsed > 0 else 0
            remaining = (total - skipped - done) / rate if rate > 0 else 0
            print(
                f"  [{done}/{total - skipped}] {pct:.1f}% | "
                f"elapsed {_fmt(elapsed)} | ETA {_fmt(remaining)} | {rate:.0f}/s"
            )

    if batch:
        conn.executemany(
            "INSERT OR REPLACE INTO chemicals "
            "(chebi_id, primary_id, label, description, equiv_ids, smiles) "
            "VALUES (?,?,?,?,?,?)",
            batch,
        )
        conn.commit()
        done += len(batch)

    elapsed = time.monotonic() - t0
    print(f"[chemicals] Done — {done:,} inserted, {skipped:,} skipped ({_fmt(elapsed)})")


def build_synonyms(conn: sqlite3.Connection,
                   synonyms_path: Path,
                   batch_size: int = 10_000) -> None:

    print(f"[synonyms] Loading {synonyms_path} ...")
    with open(synonyms_path, encoding="utf-8") as f:
        synonym_map: dict = json.load(f)

    print("[synonyms] Clearing existing synonyms table ...")
    conn.execute("DELETE FROM synonyms")
    conn.commit()

    rows: list[tuple[str, str, str]] = []
    for raw_name, chebi_dict in synonym_map.items():
        orig_name = _HTML_TAG.sub('', raw_name).strip()
        lower = orig_name.lower()
        for chebi_id in chebi_dict:
            rows.append((lower, orig_name, chebi_id))

    total = len(rows)
    print(f"[synonyms] {total:,} rows to insert")

    t0 = time.monotonic()
    done = 0
    for i in range(0, total, batch_size):
        chunk = rows[i: i + batch_size]
        conn.executemany(
            "INSERT OR IGNORE INTO synonyms (synonym_lower, orig_name, chebi_id) VALUES (?,?,?)",
            chunk,
        )
        conn.commit()
        done += len(chunk)
        elapsed = time.monotonic() - t0
        pct = 100 * done / total
        rate = done / elapsed if elapsed > 0 else 0
        remaining = (total - done) / rate if rate > 0 else 0
        print(
            f"  [{done}/{total}] {pct:.1f}% | "
            f"elapsed {_fmt(elapsed)} | ETA {_fmt(remaining)} | {rate:.0f}/s"
        )

    elapsed = time.monotonic() - t0
    print(f"[synonyms] Done — {done:,} rows inserted ({_fmt(elapsed)})")


# ---------------------------------------------------------------------------
# Vehicle override section (uses normalize_chemical pipeline, requires internet)
# ---------------------------------------------------------------------------

def _upsert_vehicle(conn: sqlite3.Connection,
                    meaning: str, primary_id: str, label: str,
                    description: str | None, equiv_id_objs: list[dict],
                    smiles: str | None) -> None:
    ids = [e["identifier"] for e in equiv_id_objs]
    if meaning not in ids:
        equiv_id_objs = [{"identifier": meaning, "label": label, "description": description}] + equiv_id_objs
    conn.execute(
        "INSERT OR REPLACE INTO chemicals "
        "(chebi_id, primary_id, label, description, equiv_ids, smiles) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (meaning, primary_id, label, description, json.dumps(equiv_id_objs), smiles),
    )
    conn.commit()
    print(
        f"  -> Saved {meaning}\n"
        f"     primary_id={primary_id!r}  label={label!r}\n"
        f"     smiles={'yes' if smiles else 'no'}  "
        f"description={'yes' if description else 'no'}"
    )


def _process_vehicle_meaning(conn: sqlite3.Connection, meaning: str) -> None:
    result = normalize_curie(meaning)
    if not result["normalized"]:
        print(f"  [NodeNorm] No result — storing minimal placeholder")
        _upsert_vehicle(conn, meaning, meaning, meaning.split(":", 1)[-1], None,
                        [{"identifier": meaning, "label": None, "description": None}], None)
        return

    primary_id = result["primary_id"]
    label = result["label"] or meaning
    description = result.get("description")
    equiv_id_objs = [
        {"identifier": e["identifier"], "label": e.get("label"), "description": e.get("description")}
        for e in result.get("equivalent_identifiers", [])
    ]

    smiles = None
    vis_curie = find_visualizable_curie(result["equivalent_identifiers"])
    if vis_curie:
        print(f"  [visualize] Found visualizable CURIE: {vis_curie}")
        vis = visualize_chemical(vis_curie)
        if vis.get("available"):
            smiles = vis.get("smiles")
        else:
            print(f"  [visualize] Not available: {vis.get('reason')}")
    else:
        print(f"  [visualize] No visualizable CURIE in equiv_ids")

    _upsert_vehicle(conn, meaning, primary_id, label, description, equiv_id_objs, smiles)


def build_vehicle_overrides(conn: sqlite3.Connection,
                             meanings: list[str] = VEHICLE_OVERRIDE_MEANINGS) -> None:
    """
    Normalize each non-CHEBI vehicle meaning via the normalize_chemical pipeline
    (NodeNorm + pubchempy for structure images) and upsert into the chemicals table.
    Requires internet access.
    """
    print(f"\n[vehicles] Processing {len(meanings)} non-CHEBI vehicle meanings …")
    for meaning in meanings:
        print(f"\n  [{meaning}]")
        try:
            _process_vehicle_meaning(conn, meaning)
        except Exception as exc:
            print(f"  ERROR: {exc} — skipping")
    print(f"\n[vehicles] Done — {len(meanings)} vehicle override(s) processed.")


# ---------------------------------------------------------------------------
# Top-level build
# ---------------------------------------------------------------------------

def build_cache(normalized: Path = DEFAULT_NORMALIZED,
                synonyms: Path = DEFAULT_SYNONYMS,
                obo: Path = DEFAULT_OBO,
                output: Path = DEFAULT_OUTPUT,
                resume: bool = False,
                skip_obo: bool = False,
                skip_vehicles: bool = False,
                test_limit: int | None = None) -> int:
    """
    Main build function. Returns 0 on success, 1 on missing input file.
    Can be called as a library function as well as from CLI.
    """
    for path, label in [(normalized, "--normalized"), (synonyms, "--synonyms")]:
        if not path.exists():
            print(f"ERROR: {label} file not found: {path}")
            return 1
    if not skip_obo and not obo.exists():
        print(f"ERROR: --obo file not found: {obo}")
        return 1

    output.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(output))
    conn.executescript(SCHEMA)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    smiles_map: dict[str, str] = {}
    if not skip_obo:
        smiles_map = parse_obo_smiles(obo)

    build_chemicals(conn, normalized, smiles_map, resume=resume, test_limit=test_limit)
    build_synonyms(conn, synonyms)

    if not skip_vehicles:
        build_vehicle_overrides(conn)

    conn.close()
    print(f"\n[done] Cache written to {output}")
    return 0


def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="Build ChEBI + vehicle SQLite cache from local data files."
    )
    parser.add_argument("--normalized", type=Path, default=DEFAULT_NORMALIZED, metavar="PATH")
    parser.add_argument("--synonyms", type=Path, default=DEFAULT_SYNONYMS, metavar="PATH")
    parser.add_argument("--obo", type=Path, default=DEFAULT_OBO, metavar="PATH")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, metavar="PATH")
    parser.add_argument("--resume", action="store_true",
                        help="Skip chebi_ids already in DB chemicals table")
    parser.add_argument("--skip-obo", action="store_true",
                        help="Skip OBO SMILES parsing (no smiles column data)")
    parser.add_argument("--skip-vehicles", action="store_true",
                        help="Skip NodeNorm vehicle override step (offline builds)")
    parser.add_argument("--test-limit", type=int, default=None, metavar="N",
                        help="Only process first N entries from normalized JSON")
    args = parser.parse_args()

    raise SystemExit(build_cache(
        normalized=args.normalized,
        synonyms=args.synonyms,
        obo=args.obo,
        output=args.output,
        resume=args.resume,
        skip_obo=args.skip_obo,
        skip_vehicles=args.skip_vehicles,
        test_limit=args.test_limit,
    ))


if __name__ == "__main__":
    _cli()
