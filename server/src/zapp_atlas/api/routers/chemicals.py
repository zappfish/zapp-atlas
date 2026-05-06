"""Chemical normalization and lookup endpoints.

GET /chemicals/autocomplete?q=...&limit=5
    Name-based autocomplete against the local ChEBI/vehicle SQLite cache.

GET /chemicals/vehicle-info?meaning=CHEBI:16236
    Local-cache lookup for a vehicle meaning CURIE; never hits external APIs.

POST /chemicals/normalize
    Normalize a chemical by name or (namespace, id) pair via NodeNorm /
    SRI Name Resolver, with local-cache fallback.
"""

from __future__ import annotations

import base64
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Path config — allow override via env var for deployment / testing
# ---------------------------------------------------------------------------

_SERVER_DIR = Path(__file__).resolve().parents[4]  # server/src/zapp_atlas/api/routers -> server/
_REPO_ROOT = _SERVER_DIR.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"

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


# ---------------------------------------------------------------------------
# Import normalize_chemical functions from the scripts directory
# ---------------------------------------------------------------------------

if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

try:
    from normalize_chemical import (  # type: ignore[import]
        find_visualizable_curie,
        lookup as _chem_lookup,
        normalize_curie,
        visualize_chemical,
    )
    _NORMALIZE_AVAILABLE = True
except ImportError:
    _NORMALIZE_AVAILABLE = False


# ---------------------------------------------------------------------------
# SMILES → SVG helper
# ---------------------------------------------------------------------------

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

def _db_lookup_by_id(chebi_id: str) -> dict | None:
    db = _get_db()
    if db is None:
        return None
    row = db.execute(
        "SELECT primary_id, label, description, equiv_ids, smiles "
        "FROM chemicals WHERE chebi_id = ?",
        (chebi_id,),
    ).fetchone()
    if row is None:
        return None
    return {
        "normalized": True,
        "primary_id": row["primary_id"],
        "label": row["label"],
        "description": row["description"],
        "biolink_type": None,
        "equivalent_identifiers": json.loads(row["equiv_ids"] or "[]"),
        "_smiles": row["smiles"],
    }


def _db_autocomplete(q: str, limit: int) -> list[dict]:
    db = _get_db()
    if db is None:
        return []
    rows = db.execute(
        "SELECT s.orig_name, c.primary_id, c.label, c.description, c.equiv_ids, c.smiles "
        "FROM synonyms s JOIN chemicals c ON s.chebi_id = c.chebi_id "
        "WHERE s.synonym_lower LIKE ? "
        "ORDER BY length(s.synonym_lower) LIMIT ?",
        (f"{q.lower()}%", limit),
    ).fetchall()
    results = []
    for row in rows:
        normalized = {
            "normalized": True,
            "primary_id": row["primary_id"],
            "label": row["label"],
            "description": row["description"],
            "biolink_type": None,
            "equivalent_identifiers": json.loads(row["equiv_ids"] or "[]"),
        }
        results.append({"input_name": row["orig_name"], "normalized": normalized})
    return results


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/chemicals", tags=["chemicals"])


@router.get("/autocomplete")
def autocomplete_chemical(
    q: str = Query(default="", min_length=0),
    limit: int = Query(default=5, ge=1, le=50),
) -> list[dict[str, Any]]:
    if len(q) < 2:
        return []
    return _db_autocomplete(q, limit)


@router.get("/vehicle-info")
def vehicle_info(meaning: str = Query(..., description="Vehicle meaning CURIE, e.g. CHEBI:16236")) -> dict[str, Any]:
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
        # Non-CHEBI vehicle rows are keyed by their meaning CURIE in chebi_id
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


# ---------------------------------------------------------------------------
# Normalize request / response models
# ---------------------------------------------------------------------------

class NormalizeRequest(BaseModel):
    namespace: Optional[str] = None
    chemical_id: Optional[str] = None
    name: Optional[str] = None


@router.post("/normalize")
def normalize_chemical_endpoint(body: NormalizeRequest) -> dict[str, Any]:
    namespace = (body.namespace or "").strip()
    chemical_id = (body.chemical_id or "").strip()
    name = (body.name or "").strip()

    use_name = bool(name) and not namespace and not chemical_id

    if not use_name and (not namespace or not chemical_id):
        raise HTTPException(
            status_code=400,
            detail="Provide either 'name' or both 'namespace' and 'chemical_id'",
        )

    if not _NORMALIZE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Chemical normalization unavailable: normalize_chemical module not found",
        )

    try:
        if use_name:
            data = _chem_lookup(name, hits=1)
        else:
            curie = f"{namespace}:{chemical_id}"
            raw = normalize_curie(curie)
            data = {
                "query": {"input": curie, "namespace": namespace, "mode": "id"},
                "meta": {"source": "nodenom"},
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


def _local_fallback(
    namespace: str, chemical_id: str, name: str, error: str | None = None
) -> dict[str, Any]:
    """Fall back to the local SQLite cache when NodeNorm is unavailable."""
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


def _get_image(result: dict) -> tuple[str | None, str | None]:
    """Extract a structure image from a normalize result dict."""
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
    if _NORMALIZE_AVAILABLE and equiv:
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
