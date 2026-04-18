"""OLS HTTP client with in-process LRU cache.

Thin wrapper around the EBI OLS4 API. Used by:
  * Autocomplete proxies in ``api.routers.ols``
  * Server-side validation in ``api.services.exposures`` when an
    ``ExposureRoute`` / ``ExposureType`` term arrives on a POST

Policy:
  * Unknown term → ``OntologyInvalidTerm`` (caller turns into 422)
  * Term exists but not reachable from required roots →
    ``OntologyInvalidTerm``
  * OLS itself unavailable (network error, 5xx, etc.) →
    ``OntologyBackendError`` (caller may fail-open)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from urllib.parse import quote

import httpx


OLS_BASE_URL = os.getenv("OLS_BASE_URL", "https://www.ebi.ac.uk/ols4/api")

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class OntologyHit:
    term_uri: str  # OBO CURIE, e.g. "ExO:0000057"
    term_label: str


class OntologyBackendError(RuntimeError):
    """OLS is unreachable or returned an unexpected shape. Caller decides
    fail-open vs fail-closed."""


class OntologyInvalidTerm(ValueError):
    """Term is unknown in the ontology or not reachable from required roots."""


def _iri_from_curie(curie: str) -> str:
    # ``ExO:0000057`` → ``http://purl.obolibrary.org/obo/ExO_0000057``
    prefix, _, local = curie.partition(":")
    return f"http://purl.obolibrary.org/obo/{prefix}_{local}"


# Module-level caches. Terms don't change within a process lifetime.
_term_cache: dict[tuple[str, str], OntologyHit] = {}
_ancestors_cache: dict[tuple[str, str], frozenset[str]] = {}


def _get(path: str, params: dict | None = None) -> httpx.Response:
    try:
        with httpx.Client(timeout=10.0) as client:
            return client.get(f"{OLS_BASE_URL}{path}", params=params)
    except httpx.HTTPError as exc:
        raise OntologyBackendError(f"OLS request failed: {exc}") from exc


def ols_search(q: str, *, ontology: str, rows: int = 10) -> list[OntologyHit]:
    resp = _get(
        "/search",
        {"q": q, "ontology": ontology, "rows": rows, "type": "class"},
    )
    if resp.status_code != 200:
        raise OntologyBackendError(f"OLS search returned {resp.status_code}")
    body = resp.json()
    hits = body.get("response", {}).get("docs", [])
    results: list[OntologyHit] = []
    for h in hits:
        term_uri = h.get("obo_id")
        term_label = h.get("label")
        if term_uri and term_label:
            results.append(OntologyHit(term_uri=term_uri, term_label=term_label))
    return results


def ols_fetch_term(curie: str, *, ontology: str) -> OntologyHit:
    key = (curie, ontology)
    if key in _term_cache:
        return _term_cache[key]

    iri = _iri_from_curie(curie)
    resp = _get(f"/ontologies/{ontology}/terms", {"iri": iri})
    if resp.status_code == 404:
        raise OntologyInvalidTerm(f"{curie} not found in {ontology}")
    if resp.status_code != 200:
        raise OntologyBackendError(f"OLS term lookup returned {resp.status_code}")

    terms = resp.json().get("_embedded", {}).get("terms", [])
    if not terms:
        raise OntologyInvalidTerm(f"{curie} not found in {ontology}")
    term = terms[0]
    hit = OntologyHit(
        term_uri=term.get("obo_id") or curie,
        term_label=term.get("label") or "",
    )
    _term_cache[key] = hit
    return hit


def ols_ancestors(curie: str, *, ontology: str) -> frozenset[str]:
    key = (curie, ontology)
    if key in _ancestors_cache:
        return _ancestors_cache[key]

    iri = _iri_from_curie(curie)
    # OLS ancestors endpoint requires the IRI path segment to be
    # double-URL-encoded.
    encoded = quote(quote(iri, safe=""), safe="")
    resp = _get(f"/ontologies/{ontology}/terms/{encoded}/ancestors", {"size": 500})
    if resp.status_code != 200:
        raise OntologyBackendError(f"OLS ancestors returned {resp.status_code}")

    terms = resp.json().get("_embedded", {}).get("terms", [])
    ancestors = frozenset(t.get("obo_id") for t in terms if t.get("obo_id"))
    _ancestors_cache[key] = ancestors
    return ancestors


def validate_and_fetch(
    curie: str,
    *,
    ontology: str,
    required_ancestors: list[str] | None = None,
) -> OntologyHit:
    """Confirm ``curie`` exists in ``ontology`` and, if provided, that at
    least one of ``required_ancestors`` is in its ancestor closure (or
    matches the term itself). Returns the canonical term.

    Raises ``OntologyInvalidTerm`` on miss / unreachable.
    Raises ``OntologyBackendError`` on network / 5xx.
    """
    term = ols_fetch_term(curie, ontology=ontology)
    if required_ancestors:
        if curie in required_ancestors:
            return term
        ancestors = ols_ancestors(curie, ontology=ontology)
        if not any(root in ancestors for root in required_ancestors):
            raise OntologyInvalidTerm(
                f"{curie} is not reachable from any of "
                f"{required_ancestors} in {ontology}"
            )
    return term


def _reset_caches_for_testing() -> None:
    _term_cache.clear()
    _ancestors_cache.clear()
