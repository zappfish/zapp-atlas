"""OLS-backed autocomplete proxies.

Same pattern as ``/zfin/fish-autocomplete``: the client never talks to OLS
directly, and we normalize the response shape to
``[{term_uri, term_label}, ...]``.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from server.ontology import (
    OntologyBackendError,
    OntologyHit,
    ols_search,
)


router = APIRouter(prefix="/ols", tags=["ols"])


def _search(ontology: str, q: str) -> list[OntologyHit]:
    try:
        return ols_search(q, ontology=ontology)
    except OntologyBackendError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OLS upstream error: {exc}",
        ) from exc


@router.get("/exposure-route-autocomplete")
def exposure_route_autocomplete(q: str = Query(..., min_length=1)) -> list[dict]:
    return [{"term_uri": h.term_uri, "term_label": h.term_label} for h in _search("exo", q)]


@router.get("/exposure-type-autocomplete")
def exposure_type_autocomplete(q: str = Query(..., min_length=1)) -> list[dict]:
    return [{"term_uri": h.term_uri, "term_label": h.term_label} for h in _search("ecto", q)]
