"""Chemical normalization and lookup FastAPI router.

GET  /api/chemicals/autocomplete?q=...&limit=5
GET  /api/chemicals/vehicle-info?meaning=CHEBI:16236
POST /api/chemicals/normalize   body: {namespace, chemical_id} or {name}
"""

from __future__ import annotations

import base64
import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from zapp_atlas.chem.normalize import (
    find_visualizable_curie,
    lookup as _chem_lookup,
    normalize_curie,
    visualize_chemical,
)

_REPO_ROOT = Path(__file__).resolve().parents[5]
_DEFAULT_CACHE = _REPO_ROOT / "zfin_test_data" / "chebi_and_vehicle_cache.db"


def _cache_path() -> Path:
    env = os.getenv("ZAPP_CHEM_CACHE_PATH")
    return Path(env).resolve() if env else _DEFAULT_CACHE


# ---------------------------------------------------------------------------
# Lazy SQLite cache handle
# ---------------------------------------------------------------------------

_chebi_db: sqlite3.Connection | None = None


def _get_db() -> sqlite3.Connection | None:
    global _chebi_db
    if _chebi_db is not None:
        return _chebi_db
    path = _cache_path()
    if not path.exists():
        return None
    _chebi_db = sqlite3.connect(str(path), check_same_thread=False)
    _chebi_db.row_factory = sqlite3.Row
    return _chebi_db


def _smiles_to_svg_b64(smiles: str | None) -> str | None:
    if not smiles:
        return None
    try:
        from rdkit import Chem
        from rdkit.Chem.Draw import rdMolDraw2D

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        drawer = rdMolDraw2D.MolDraw2DSVG(300, 300)
        drawer.drawOptions().addStereoAnnotation = False
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText()
        return base64.b64encode(svg.encode()).decode("ascii")
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Shared DB helpers
# ---------------------------------------------------------------------------

def _db_autocomplete(q: str, limit: int) -> list[dict]:
    db = _get_db()
    if db is None:
        return []
    q_lower = q.lower()
    # BETWEEN range forces idx_syn_lower usage; LIKE with a ? parameter causes a full scan.
    # Increment the last character to form the exclusive upper bound (chemical names are ASCII).
    prefix_hi = q_lower[:-1] + chr(ord(q_lower[-1]) + 1)
    rows = db.execute(
        "SELECT s.orig_name, s.chebi_id, c.primary_id, c.label, c.description, c.equiv_ids "
        "FROM synonyms s JOIN chemicals c ON s.chebi_id = c.chebi_id "
        "WHERE s.synonym_lower >= ? AND s.synonym_lower < ? "
        "ORDER BY length(s.synonym_lower), s.orig_name "
        "LIMIT ?",
        (q_lower, prefix_hi, limit * 100),
    ).fetchall()

    groups: dict[str, dict] = {}
    for row in rows:
        name = row["orig_name"]
        if name not in groups:
            groups[name] = {"chebi_ids": [], "normalized": None}
        groups[name]["chebi_ids"].append(row["chebi_id"])
        if groups[name]["normalized"] is None or row["chebi_id"] == row["primary_id"]:
            groups[name]["normalized"] = {
                "normalized": True,
                "primary_id": row["primary_id"],
                "label": row["label"],
                "description": row["description"],
                "biolink_type": None,
                "equivalent_identifiers": json.loads(row["equiv_ids"] or "[]"),
            }
        if len(groups) >= limit:
            break

    return [
        {"name": name, "chebi_ids": data["chebi_ids"], "normalized": data["normalized"]}
        for name, data in groups.items()
    ]


def _get_image(result: dict) -> tuple[str | None, str | None]:
    primary = result.get("primary_id") or ""
    smiles = None

    db = _get_db()
    if primary.startswith("CHEBI:") and db:
        row = db.execute(
            "SELECT smiles FROM chemicals WHERE chebi_id = ?", (primary,)
        ).fetchone()
        if row:
            smiles = row[0]

    if smiles:
        b64 = _smiles_to_svg_b64(smiles)
        if b64:
            return b64, "svg"

    equiv = result.get("equivalent_identifiers", [])
    if equiv:
        vis = find_visualizable_curie(equiv)
        if vis:
            try:
                vis_result = visualize_chemical(vis)
                if vis_result.get("available") and vis_result.get("smiles"):
                    b64 = _smiles_to_svg_b64(vis_result["smiles"])
                    if b64:
                        return b64, "svg"
            except Exception:
                pass

    return None, None


def _local_fallback(namespace: str, chemical_id: str, name: str, error: str | None = None) -> dict:
    db = _get_db()
    result = None
    smiles = None

    if db is not None:
        if namespace == "CHEBI" and chemical_id:
            row = db.execute(
                "SELECT primary_id, label, description, equiv_ids, smiles "
                "FROM chemicals WHERE chebi_id = ?",
                (f"CHEBI:{chemical_id}",),
            ).fetchone()
            if row:
                result = {
                    "normalized": True,
                    "primary_id": row["primary_id"],
                    "label": row["label"],
                    "description": row["description"],
                    "biolink_type": None,
                    "equivalent_identifiers": json.loads(row["equiv_ids"] or "[]"),
                }
                smiles = row["smiles"]
        elif name:
            hits = _db_autocomplete(name, 5)
            if hits and hits[0].get("normalized", {}).get("normalized"):
                result = hits[0]["normalized"]

    if result is None:
        result = {
            "normalized": False,
            "primary_id": None,
            "label": None,
            "description": None,
            "biolink_type": None,
            "equivalent_identifiers": [],
        }

    image_b64 = _smiles_to_svg_b64(smiles)
    return {
        "query": {"input": chemical_id or name, "namespace": namespace or None, "mode": "id" if namespace else "name"},
        "meta": {"source": "local_cache", **({"error": error} if error else {})},
        "result": result,
        "results": [result] if result["normalized"] else [],
        "structure_image_b64": image_b64,
        "structure_image_type": "svg" if image_b64 else None,
    }


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/chemicals", tags=["chemicals"])


@router.get("/autocomplete")
def autocomplete_chemical(
    q: str = Query(default=""),
    limit: int = Query(default=5, ge=1, le=50),
) -> list[dict[str, Any]]:
    q = q.strip()
    if len(q) < 2:
        return []
    return _db_autocomplete(q, limit)


@router.get("/vehicle-info")
def vehicle_info(meaning: str = Query(default="")) -> dict[str, Any]:
    meaning = meaning.strip()
    if not meaning or ":" not in meaning:
        raise HTTPException(status_code=400, detail="Provide a 'meaning' CURIE, e.g. CHEBI:16236")

    db = _get_db()
    if db is None:
        return {"found": False}

    ns = meaning.split(":", 1)[0]
    if ns == "CHEBI":
        row = db.execute(
            "SELECT primary_id, label, description, equiv_ids, smiles "
            "FROM chemicals WHERE chebi_id = ?",
            (meaning,),
        ).fetchone()
    else:
        row = db.execute(
            "SELECT primary_id, label, description, equiv_ids, smiles "
            "FROM chemicals WHERE chebi_id = ? OR equiv_ids LIKE ?",
            (meaning, f"%{meaning}%"),
        ).fetchone()

    if row is None:
        return {"found": False}

    result = {
        "normalized": True,
        "primary_id": row["primary_id"],
        "label": row["label"],
        "description": row["description"],
        "biolink_type": None,
        "equivalent_identifiers": json.loads(row["equiv_ids"] or "[]"),
    }
    image_b64 = _smiles_to_svg_b64(row["smiles"])
    return {
        "found": True,
        "result": result,
        "structure_image_b64": image_b64,
        "structure_image_type": "svg" if image_b64 else None,
    }


class NormalizeRequest(BaseModel):
    namespace: str = ""
    chemical_id: str = ""
    name: str = ""


@router.post("/normalize")
def normalize_chemical_endpoint(body: NormalizeRequest) -> dict[str, Any]:
    namespace = body.namespace.strip()
    chemical_id = body.chemical_id.strip()
    name = body.name.strip()

    use_name = bool(name) and not namespace and not chemical_id

    if not use_name and (not namespace or not chemical_id):
        raise HTTPException(
            status_code=400,
            detail="Provide either 'name' or both 'namespace' and 'chemical_id'",
        )

    try:
        if use_name:
            data = _chem_lookup(name, hits=5)
        else:
            curie = f"{namespace}:{chemical_id}"
            raw = normalize_curie(curie)
            data = {
                "query": {"input": curie, "namespace": namespace, "mode": "id"},
                "meta": {"source": "nodenorm"},
                "result": raw,
                "results": [raw] if raw.get("normalized") else [],
            }
    except Exception as exc:
        return _local_fallback(namespace, chemical_id, name, error=str(exc))

    result = data.get("result", {})
    if not result.get("normalized"):
        return _local_fallback(namespace, chemical_id, name)

    image_b64, image_type = _get_image(result)
    return {**data, "structure_image_b64": image_b64, "structure_image_type": image_type}
