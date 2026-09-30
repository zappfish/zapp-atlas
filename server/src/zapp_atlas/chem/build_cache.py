"""Build the chemical cache that backs ``/api/chemicals`` (see ``chem.cache``).

Inputs, all in ``--input-dir`` (default ``db/data/chebi/``):

* ``chebi_normalized.json`` and ``chebi_synonym_mapping.json`` — written by
  ``python -m zapp_atlas.chem.precompute``
* ``chebi.obo`` — the ChEBI ontology, read only for its SMILES strings

Then, unless ``--skip-vehicles``, each ``VehicleEnum`` meaning outside ChEBI
(PBS, BSA, ...) is normalized through NodeNorm and given a row of its own, so
the vehicle picker can show it. That step needs the network.

    uv run python -m zapp_atlas.chem.build_cache
    uv run python -m zapp_atlas.chem.build_cache --resume --test-limit 1000
    uv run python -m zapp_atlas.chem.build_cache --skip-vehicles   # offline
"""

import argparse
import json
import re
import sqlite3
import time
from pathlib import Path

import yaml

from zapp_atlas.chem.cache import SCHEMA
from zapp_atlas.chem.normalize import fetch_smiles, find_visualizable_curie, normalize_curie
from zapp_atlas.chem.precompute import DEFAULT_INPUT_DIR
from zapp_atlas.settings import DEFAULT_CHEM_CACHE_PATH

CHEMICAL_ENUMS = Path(__file__).resolve().parents[1] / "schema" / "chemical_enums.yaml"

_HTML_TAG = re.compile(r"<[^>]+>")
_SMILES_PREFIX = 'property_value: chemrof:smiles_string "'
_INSERT_CHEMICAL = (
    "INSERT OR REPLACE INTO chemicals "
    "(chebi_id, primary_id, label, description, equiv_ids, smiles) VALUES (?,?,?,?,?,?)"
)


def _fmt(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m{s:02d}s" if h else f"{m}m{s:02d}s" if m else f"{s}s"


def vehicle_meanings() -> list[str]:
    """The ``VehicleEnum`` meanings the ChEBI data will not cover."""
    enums = yaml.safe_load(CHEMICAL_ENUMS.read_text())["enums"]
    values = enums["VehicleEnum"]["permissible_values"].values()
    return [
        v["meaning"]
        for v in values
        if v and v.get("meaning") and not v["meaning"].startswith("CHEBI:")
    ]


def parse_obo_smiles(obo_path: Path) -> dict[str, str]:
    """Stream chebi.obo and collect CHEBI ID -> SMILES."""
    print(f"[OBO] Parsing SMILES from {obo_path} ...")
    t0 = time.monotonic()
    smiles: dict[str, str] = {}
    current_id: str | None = None
    with obo_path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("[Term]"):
                current_id = None
            elif line.startswith("id: CHEBI:"):
                current_id = line[4:].strip()
            elif current_id and line.startswith(_SMILES_PREFIX):
                rest = line[len(_SMILES_PREFIX) :]
                end = rest.find('"')
                if end != -1:
                    smiles[current_id] = rest[:end]
    print(f"[OBO] {len(smiles):,} SMILES ({_fmt(time.monotonic() - t0)})")
    return smiles


def build_chemicals(
    conn: sqlite3.Connection,
    normalized_path: Path,
    smiles: dict[str, str],
    resume: bool,
    test_limit: int | None,
    batch_size: int = 500,
) -> None:
    print(f"[chemicals] Loading {normalized_path} ...")
    with normalized_path.open(encoding="utf-8") as f:
        entries = list(json.load(f).items())
    if test_limit is not None:
        entries = entries[:test_limit]
    if resume:
        existing = {row[0] for row in conn.execute("SELECT chebi_id FROM chemicals")}
        entries = [(k, v) for k, v in entries if k not in existing]
        print(f"[chemicals] Resuming: skipping {len(existing):,} already in the cache")

    t0 = time.monotonic()
    for i in range(0, len(entries), batch_size):
        conn.executemany(
            _INSERT_CHEMICAL,
            [
                (
                    chebi_id,
                    result.get("primary_id"),
                    result.get("label"),
                    result.get("description"),
                    json.dumps(result.get("equivalent_identifiers") or []),
                    smiles.get(chebi_id),
                )
                for chebi_id, result in entries[i : i + batch_size]
            ],
        )
        conn.commit()
    print(f"[chemicals] {len(entries):,} inserted ({_fmt(time.monotonic() - t0)})")


def build_synonyms(conn: sqlite3.Connection, synonyms_path: Path) -> None:
    print(f"[synonyms] Loading {synonyms_path} ...")
    with synonyms_path.open(encoding="utf-8") as f:
        synonym_map: dict[str, dict[str, str]] = json.load(f)

    t0 = time.monotonic()
    conn.execute("DELETE FROM synonyms")
    rows = []
    for raw_name, chebi_ids in synonym_map.items():
        name = _HTML_TAG.sub("", raw_name).strip()
        rows.extend((name.lower(), name, chebi_id) for chebi_id in chebi_ids)
    conn.executemany(
        "INSERT OR IGNORE INTO synonyms (synonym_lower, orig_name, chebi_id) VALUES (?,?,?)",
        rows,
    )

    # ChEBI's names file lists synonyms, IUPAC names, and brand names, but
    # never a term's own name. Autocomplete searches only this table, so add
    # each primary label too.
    labels = conn.execute(
        "INSERT OR IGNORE INTO synonyms (synonym_lower, orig_name, chebi_id) "
        "SELECT lower(label), label, chebi_id FROM chemicals WHERE label IS NOT NULL "
        "AND label != ''"
    ).rowcount
    conn.commit()
    print(
        f"[synonyms] {len(rows):,} synonyms + {labels:,} primary labels "
        f"({_fmt(time.monotonic() - t0)})"
    )


def add_vehicle(conn: sqlite3.Connection, meaning: str) -> None:
    result = normalize_curie(meaning)
    if not result["normalized"]:
        print(f"  {meaning}: not in NodeNorm; storing a placeholder")
        label = meaning.split(":", 1)[-1]
        equivs = [{"identifier": meaning, "label": None, "description": None}]
        conn.execute(_INSERT_CHEMICAL, (meaning, meaning, label, None, json.dumps(equivs), None))
        conn.commit()
        return

    label = result["label"] or meaning
    equivs = result["equivalent_identifiers"]
    if meaning not in {e["identifier"] for e in equivs}:
        equivs = [{"identifier": meaning, "label": label, "description": result["description"]}]
        equivs += result["equivalent_identifiers"]
    curie = find_visualizable_curie(equivs)
    smiles = None
    if curie:
        try:
            smiles = fetch_smiles(curie)
        except Exception as exc:
            print(f"  {meaning}: no structure, PubChem lookup failed ({exc})")
    conn.execute(
        _INSERT_CHEMICAL,
        (meaning, result["primary_id"], label, result["description"], json.dumps(equivs), smiles),
    )
    conn.commit()
    print(f"  {meaning}: {label!r} (structure: {'yes' if smiles else 'no'})")


def build_vehicles(conn: sqlite3.Connection) -> None:
    meanings = vehicle_meanings()
    print(f"[vehicles] {len(meanings)} non-ChEBI vehicle meanings")
    for meaning in meanings:
        try:
            add_vehicle(conn, meaning)
        except Exception as exc:
            print(f"  {meaning}: ERROR {exc} — skipped")


def main() -> int:
    p = argparse.ArgumentParser(
        description="Build the chemical cache from precomputed ChEBI data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    p.add_argument("--output", type=Path, default=DEFAULT_CHEM_CACHE_PATH)
    p.add_argument("--resume", action="store_true", help="Keep chemicals already in the cache")
    p.add_argument("--skip-obo", action="store_true", help="Build without SMILES")
    p.add_argument("--skip-vehicles", action="store_true", help="Skip the NodeNorm vehicle step")
    p.add_argument("--test-limit", type=int, default=None, help="Only load the first N chemicals")
    args = p.parse_args()

    normalized = args.input_dir / "chebi_normalized.json"
    synonyms = args.input_dir / "chebi_synonym_mapping.json"
    obo = args.input_dir / "chebi.obo"
    required = [normalized, synonyms] + ([] if args.skip_obo else [obo])
    missing = [path for path in required if not path.exists()]
    if missing:
        for path in missing:
            print(f"ERROR: input not found: {path}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(args.output)
    try:
        conn.executescript(SCHEMA)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        smiles = {} if args.skip_obo else parse_obo_smiles(obo)
        build_chemicals(conn, normalized, smiles, args.resume, args.test_limit)
        build_synonyms(conn, synonyms)
        if not args.skip_vehicles:
            build_vehicles(conn)
        # The API opens the cache read-only, which a WAL database does not
        # reliably allow; WAL was only for the speed of the bulk load.
        conn.execute("PRAGMA journal_mode=DELETE")
    finally:
        conn.close()
    print(f"\n[done] Cache written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
