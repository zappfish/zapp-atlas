"""Chemical lookup for the editing form's substance and vehicle pickers.

Normalization asks NodeNorm first, since it is current and covers every
namespace, and falls back to the local ChEBI cache when the service is
unreachable or does not know the identifier. Autocomplete and vehicle lookups
are served from the cache alone: they run on every keystroke or selection and
must not wait on the network.

Results carry no structure diagrams. The atlas is for biologists, who identify
a chemical by name and identifier, and rendering diagrams server-side took
rdkit, numpy, and pillow (~270 MB installed). If they are wanted later, PubChem
serves ready-made images (``/rest/pug/compound/cid/<cid>/PNG``) that the client
can load directly for any result with a PubChem identifier.
"""

import logging
import sqlite3
from typing import Any

import httpx

from zapp_atlas.chem import cache, normalize

logger = logging.getLogger(__name__)


def _response(result: dict[str, Any], results: list[dict[str, Any]], source: str):
    return {"source": source, "result": result, "results": results}


def _from_cache(conn: sqlite3.Connection | None, curie: str | None, name: str | None):
    result = None
    if conn is not None:
        if curie:
            result = cache.get_chemical(conn, curie)
        elif name:
            hits = cache.autocomplete(conn, name, 5)
            if hits and hits[0]["normalized"]:
                result = hits[0]["normalized"]
    if result is None:
        return _response(normalize.empty_result(), [], "local_cache")
    return _response(result, [result], "local_cache")


def normalize_identifier(conn: sqlite3.Connection | None, curie: str) -> dict[str, Any]:
    try:
        result = normalize.normalize_curie(curie)
    except httpx.HTTPError:
        logger.warning("NodeNorm lookup failed for %s", curie, exc_info=True)
        return _from_cache(conn, curie, None)
    if not result["normalized"]:
        return _from_cache(conn, curie, None)
    return _response(result, [result], "nodenorm")


def normalize_name(conn: sqlite3.Connection | None, name: str) -> dict[str, Any]:
    try:
        results = normalize.resolve_name(name, limit=5)
    except httpx.HTTPError:
        logger.warning("Name resolution failed for %r", name, exc_info=True)
        return _from_cache(conn, None, name)
    if not results:
        return _from_cache(conn, None, name)
    return _response(results[0], results, "nodenorm")


def vehicle_info(conn: sqlite3.Connection | None, meaning: str) -> dict[str, Any]:
    result = cache.find_by_identifier(conn, meaning) if conn is not None else None
    if result is None:
        return {"found": False}
    return {"found": True, "result": result}
