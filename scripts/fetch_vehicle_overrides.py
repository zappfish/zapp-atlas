"""
Fetch NodeNorm data for non-CHEBI vehicle meanings and insert into
chebi_and_vehicle_cache.db, using the same normalize_chemical pipeline
that substances use (NodeNorm + pubchempy for structure images).

Run AFTER build_chebi_and_vehicle_cache.py (or use --copy-from to migrate
an existing chebi_cache.db before adding vehicle rows).

Usage:
    python scripts/fetch_vehicle_overrides.py
    python scripts/fetch_vehicle_overrides.py --copy-from zfin_test_data/chebi_cache.db
    python scripts/fetch_vehicle_overrides.py --db path/to/chebi_and_vehicle_cache.db
"""

import argparse
import json
import shutil
import sqlite3
import sys
from pathlib import Path

# Resolve normalize_chemical from the same scripts/ directory
_SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS_DIR))
from normalize_chemical import normalize_curie, find_visualizable_curie, visualize_chemical

_REPO_ROOT = _SCRIPTS_DIR.parent
DEFAULT_DB = _REPO_ROOT / "zfin_test_data" / "chebi_and_vehicle_cache.db"

# Non-CHEBI vehicle meanings — add new ones here when VehicleEnum gains entries
VEHICLE_MEANINGS = [
    "PUBCHEM.COMPOUND:24978514",  # Phosphate-buffered saline (PBS)
    "UMLS:C0036774",              # Bovine serum albumin (BSA)
    "UNII:3XK098O8ZW",            # Solketal
]


def _upsert(conn: sqlite3.Connection, meaning: str, primary_id: str, label: str,
            description: str | None, equiv_id_objs: list[dict], smiles: str | None) -> None:
    # equiv_id_objs must be full objects {"identifier": ..., "label": ..., "description": ...}
    # to match the CHEBI cache format that ResultCard expects.
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


def process_meaning(conn: sqlite3.Connection, meaning: str) -> None:
    result = normalize_curie(meaning)
    if not result["normalized"]:
        print(f"  [NodeNorm] No result — storing minimal placeholder")
        _upsert(conn, meaning, meaning, meaning.split(":", 1)[-1], None,
                [{"identifier": meaning, "label": None, "description": None}], None)
        return

    primary_id = result["primary_id"]
    label = result["label"] or meaning
    description = result.get("description")
    # Keep full objects so the frontend can render identifier + label columns
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
            print(f"  [visualize] SMILES: {smiles[:40]}..." if smiles and len(smiles) > 40 else f"  [visualize] SMILES: {smiles}")
        else:
            print(f"  [visualize] Not available: {vis.get('reason')}")
    else:
        print(f"  [visualize] No visualizable CURIE in equiv_ids")

    _upsert(conn, meaning, primary_id, label, description, equiv_id_objs, smiles)


def main(db_path: Path, copy_from: Path | None) -> int:
    if copy_from:
        if not copy_from.exists():
            print(f"ERROR: --copy-from path not found: {copy_from}")
            return 1
        print(f"[setup] Copying {copy_from} → {db_path}")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(copy_from, db_path)

    if not db_path.exists():
        print(f"ERROR: DB not found: {db_path}")
        print("Run scripts/build_chebi_and_vehicle_cache.py first.")
        return 1

    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row

    for meaning in VEHICLE_MEANINGS:
        print(f"\n[{meaning}]")
        process_meaning(conn, meaning)

    conn.close()
    print("\n[done] Vehicle overrides written to", db_path)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch NodeNorm/pubchempy data for non-CHEBI vehicle meanings."
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, metavar="PATH")
    parser.add_argument(
        "--copy-from", type=Path, default=None, metavar="PATH",
        help="Copy an existing chebi_cache.db to --db before inserting vehicle rows"
    )
    args = parser.parse_args()
    raise SystemExit(main(args.db, args.copy_from))
