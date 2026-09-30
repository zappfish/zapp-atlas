"""Chemical lookup for the editing form's substance and vehicle pickers.

Normalization asks NodeNorm first, since it is current and covers every
namespace, and falls back to the local ChEBI cache when the service is
unreachable or does not know the identifier. Autocomplete and vehicle lookups
go the other way: they run on every keystroke or selection, so they use the
cache when one is built and only otherwise ask the Name Resolver and NodeNorm.

The cache is optional. Without it (the deployed app has none yet) the pickers
work entirely off the live services, at the cost of a network round trip per
keystroke and no lookups while those services are down.

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


def autocomplete(conn: sqlite3.Connection | None, q: str, limit: int) -> list[dict[str, Any]]:
    if conn is not None:
        return cache.autocomplete(conn, q, limit)
    try:
        hits = normalize.autocomplete(q, limit)
    except httpx.HTTPError:
        logger.warning("Name Resolver autocomplete failed for %r", q, exc_info=True)
        return []
    # Match the cache's shape: one suggestion per name, with the ChEBI terms
    # it names. The client normalizes each of those by ID, and any other hit
    # by name, so a non-ChEBI hit carries no IDs rather than a non-ChEBI one.
    suggestions: dict[str, dict[str, Any]] = {}
    for hit in hits:
        suggestion = suggestions.setdefault(
            hit["label"], {"name": hit["label"], "chebi_ids": [], "normalized": None}
        )
        if hit["curie"].startswith("CHEBI:"):
            suggestion["chebi_ids"].append(hit["curie"])
    return list(suggestions.values())


def vehicle_info(conn: sqlite3.Connection | None, meaning: str) -> dict[str, Any]:
    result = cache.find_by_identifier(conn, meaning) if conn is not None else None
    if result is None:
        try:
            result = normalize.normalize_curie(meaning)
        except httpx.HTTPError:
            logger.warning("NodeNorm lookup failed for %s", meaning, exc_info=True)
            return {"found": False}
        if not result["normalized"]:
            return {"found": False}
    return {"found": True, "result": result}
