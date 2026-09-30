"""Chemical lookup endpoints backing the substance and vehicle pickers.

* GET  /chemicals/autocomplete?q=eth&limit=5 — names starting with ``q``
* GET  /chemicals/vehicle-info?meaning=CHEBI:16236 — a vehicle's cached details
* POST /chemicals/normalize — ``{namespace, chemical_id}`` or ``{name}``

These are read-only reference lookups against NodeNorm and the local ChEBI
cache (``ZAPP_CHEM_CACHE_PATH``); nothing here touches the application
database. Without a cache, autocomplete and vehicle-info find nothing and
normalization depends on NodeNorm being reachable.
"""

import sqlite3
from collections.abc import Iterator
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, model_validator

from zapp_atlas.api.deps import get_app_settings
from zapp_atlas.api.services import chemicals as service
from zapp_atlas.chem.cache import autocomplete, open_cache
from zapp_atlas.settings import AppSettings

router = APIRouter(prefix="/chemicals", tags=["chemicals"])


def get_chem_cache(
    settings: Annotated[AppSettings, Depends(get_app_settings)],
) -> Iterator[sqlite3.Connection | None]:
    with open_cache(settings.chem_cache_path) as conn:
        yield conn


ChemCache = Annotated[sqlite3.Connection | None, Depends(get_chem_cache)]


class EquivalentIdentifier(BaseModel):
    identifier: str | None
    label: str | None = None
    description: str | None = None


class NormResult(BaseModel):
    normalized: bool
    primary_id: str | None
    label: str | None
    description: str | None
    biolink_type: str | None
    equivalent_identifiers: list[EquivalentIdentifier]


class Suggestion(BaseModel):
    name: str
    chebi_ids: list[str]
    normalized: NormResult | None


class NormalizeRequest(BaseModel):
    namespace: str = ""
    chemical_id: str = ""
    name: str = ""

    @model_validator(mode="after")
    def _one_mode(self) -> "NormalizeRequest":
        self.namespace = self.namespace.strip()
        self.chemical_id = self.chemical_id.strip()
        self.name = self.name.strip()
        if not (self.namespace and self.chemical_id) and not self.by_name:
            raise ValueError("Provide either 'name' or both 'namespace' and 'chemical_id'")
        return self

    @property
    def by_name(self) -> bool:
        return bool(self.name) and not self.namespace and not self.chemical_id


class NormalizeResponse(BaseModel):
    source: Literal["nodenorm", "local_cache"]
    result: NormResult
    results: list[NormResult]


class VehicleInfo(BaseModel):
    found: bool
    result: NormResult | None = None


@router.get("/autocomplete", response_model=list[Suggestion])
def autocomplete_endpoint(
    conn: ChemCache,
    q: str = "",
    limit: Annotated[int, Query(ge=1, le=50)] = 5,
) -> list[dict]:
    q = q.strip()
    if len(q) < 2 or conn is None:
        return []
    return autocomplete(conn, q, limit)


@router.get("/vehicle-info", response_model=VehicleInfo)
def vehicle_info_endpoint(conn: ChemCache, meaning: str = "") -> dict:
    meaning = meaning.strip()
    if ":" not in meaning:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide a 'meaning' CURIE, e.g. CHEBI:16236",
        )
    return service.vehicle_info(conn, meaning)


@router.post("/normalize", response_model=NormalizeResponse)
def normalize_endpoint(body: NormalizeRequest, conn: ChemCache) -> dict:
    if body.by_name:
        return service.normalize_name(conn, body.name)
    return service.normalize_identifier(conn, f"{body.namespace}:{body.chemical_id}")
