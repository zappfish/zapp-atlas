"""Read access to the local chemical cache: a prebuilt SQLite file of ChEBI terms.

The cache is built offline by ``python -m zapp_atlas.chem.build_cache`` and
opened read-only here. It is separate from the application database: it holds
reference data, not anything users submit, and can be rebuilt from scratch at
any time.

Two tables:

* ``chemicals`` — one row per ChEBI term (plus a few non-ChEBI vehicle
  meanings, keyed by their own CURIE), with its NodeNorm clique and SMILES.
* ``synonyms`` — every name a term is known by, lowercased, for prefix search.
"""

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

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

_CHEMICAL_COLUMNS = "primary_id, label, description, equiv_ids, smiles"


@contextmanager
def open_cache(path: Path) -> Iterator[sqlite3.Connection | None]:
    """Open the cache read-only, or yield None if it has not been built."""
    if not path.is_file():
        yield None
        return
    conn = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _result(row: sqlite3.Row) -> dict[str, Any]:
    """Shape a ``chemicals`` row like a NodeNorm result."""
    return {
        "normalized": True,
        "primary_id": row["primary_id"],
        "label": row["label"],
        "description": row["description"],
        "biolink_type": None,
        "equivalent_identifiers": json.loads(row["equiv_ids"] or "[]"),
    }


def autocomplete(conn: sqlite3.Connection, q: str, limit: int) -> list[dict[str, Any]]:
    """Names starting with ``q``, shortest first, each with the terms it names.

    One name can belong to several ChEBI terms; they are grouped under it, and
    the term that is its own clique leader supplies the normalized result.
    """
    q_lower = q.lower()
    # A half-open range rather than LIKE: a parameterized LIKE cannot use
    # idx_syn_lower and scans the whole table.
    upper = q_lower[:-1] + chr(ord(q_lower[-1]) + 1)
    rows = conn.execute(
        f"SELECT s.orig_name, s.chebi_id, {_CHEMICAL_COLUMNS} "
        "FROM synonyms s JOIN chemicals c ON s.chebi_id = c.chebi_id "
        "WHERE s.synonym_lower >= ? AND s.synonym_lower < ? "
        "ORDER BY length(s.synonym_lower), s.orig_name "
        "LIMIT ?",
        (q_lower, upper, limit * 100),
    ).fetchall()

    groups: dict[str, dict[str, Any]] = {}
    for row in rows:
        name = row["orig_name"]
        if name not in groups:
            if len(groups) >= limit:
                break
            groups[name] = {"name": name, "chebi_ids": [], "normalized": None}
        group = groups[name]
        group["chebi_ids"].append(row["chebi_id"])
        if group["normalized"] is None or row["chebi_id"] == row["primary_id"]:
            group["normalized"] = _result(row)
    return list(groups.values())


def get_chemical(conn: sqlite3.Connection, curie: str) -> tuple[dict[str, Any], str | None] | None:
    """The cached result and SMILES for a term by its own CURIE."""
    row = conn.execute(
        f"SELECT {_CHEMICAL_COLUMNS} FROM chemicals WHERE chebi_id = ?", (curie,)
    ).fetchone()
    return (_result(row), row["smiles"]) if row else None


def find_by_identifier(
    conn: sqlite3.Connection, curie: str
) -> tuple[dict[str, Any], str | None] | None:
    """Like ``get_chemical``, but also matches a term listing ``curie`` as an equivalent."""
    found = get_chemical(conn, curie)
    if found is not None:
        return found
    row = conn.execute(
        f"SELECT {_CHEMICAL_COLUMNS} FROM chemicals "
        "WHERE EXISTS (SELECT 1 FROM json_each(equiv_ids) "
        "              WHERE json_extract(value, '$.identifier') = ?) "
        "LIMIT 1",
        (curie,),
    ).fetchone()
    return (_result(row), row["smiles"]) if row else None


def get_smiles(conn: sqlite3.Connection, curie: str) -> str | None:
    row = conn.execute("SELECT smiles FROM chemicals WHERE chebi_id = ?", (curie,)).fetchone()
    return row["smiles"] if row else None
