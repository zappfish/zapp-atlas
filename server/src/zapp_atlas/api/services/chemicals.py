"""Chemical lookup for the editing form's substance and vehicle pickers.

Normalization asks NodeNorm first, since it is current and covers every
namespace, and falls back to the local ChEBI cache when the service is
unreachable or does not know the identifier. Autocomplete and vehicle lookups
are served from the cache alone: they run on every keystroke or selection and
must not wait on the network.
"""

import base64
import logging
import sqlite3
from typing import Any

import httpx
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D

from zapp_atlas.chem import cache, normalize

logger = logging.getLogger(__name__)


def structure_svg_b64(smiles: str | None) -> str | None:
    """Render a SMILES string as a base64-encoded SVG, or None if it will not parse."""
    if not smiles:
        return None
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    drawer = rdMolDraw2D.MolDraw2DSVG(300, 300)
    drawer.drawOptions().addStereoAnnotation = False
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    return base64.b64encode(drawer.GetDrawingText().encode()).decode("ascii")


def _structure_for(conn: sqlite3.Connection | None, result: dict[str, Any]) -> str | None:
    """A structure image for a normalized result: from the cache, else from PubChem."""
    primary_id = result.get("primary_id") or ""
    smiles = cache.get_smiles(conn, primary_id) if conn is not None else None
    if not smiles:
        curie = normalize.find_visualizable_curie(result.get("equivalent_identifiers", []))
        if curie:
            try:
                smiles = normalize.fetch_smiles(curie)
            except Exception:
                logger.warning("PubChem structure lookup failed for %s", curie, exc_info=True)
    return structure_svg_b64(smiles)


def _response(
    result: dict[str, Any], results: list[dict[str, Any]], image: str | None, source: str
):
    return {
        "source": source,
        "result": result,
        "results": results,
        "structure_image_b64": image,
        "structure_image_type": "svg" if image else None,
    }


def _from_cache(conn: sqlite3.Connection | None, curie: str | None, name: str | None):
    found = None
    if conn is not None:
        if curie:
            found = cache.get_chemical(conn, curie)
        elif name:
            hits = cache.autocomplete(conn, name, 5)
            if hits and hits[0]["normalized"]:
                result = hits[0]["normalized"]
                found = (result, cache.get_smiles(conn, result["primary_id"]))
    if found is None:
        return _response(normalize.empty_result(), [], None, "local_cache")
    result, smiles = found
    return _response(result, [result], structure_svg_b64(smiles), "local_cache")


def normalize_identifier(conn: sqlite3.Connection | None, curie: str) -> dict[str, Any]:
    try:
        result = normalize.normalize_curie(curie)
    except httpx.HTTPError:
        logger.warning("NodeNorm lookup failed for %s", curie, exc_info=True)
        return _from_cache(conn, curie, None)
    if not result["normalized"]:
        return _from_cache(conn, curie, None)
    return _response(result, [result], _structure_for(conn, result), "nodenorm")


def normalize_name(conn: sqlite3.Connection | None, name: str) -> dict[str, Any]:
    try:
        results = normalize.resolve_name(name, limit=5)
    except httpx.HTTPError:
        logger.warning("Name resolution failed for %r", name, exc_info=True)
        return _from_cache(conn, None, name)
    if not results:
        return _from_cache(conn, None, name)
    return _response(results[0], results, _structure_for(conn, results[0]), "nodenorm")


def vehicle_info(conn: sqlite3.Connection | None, meaning: str) -> dict[str, Any]:
    found = cache.find_by_identifier(conn, meaning) if conn is not None else None
    if found is None:
        return {"found": False}
    result, smiles = found
    image = structure_svg_b64(smiles)
    return {
        "found": True,
        "result": result,
        "structure_image_b64": image,
        "structure_image_type": "svg" if image else None,
    }
