"""ZFIN reference lookups (public read-only data, no auth).

These endpoints serve ZFIN's own published download files back as ranked
autocomplete results, so the fish form can attach identifiers silently while
the curator only ever types names. They are reference data, not user data:
no group scoping, no writes. A 503 means the download files have not been
fetched yet (`just fetch-zfin`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from zapp_atlas.api.deps import get_app_settings
from zapp_atlas.api.dto import (
    ZfinAlleleOut,
    ZfinAlleleSearchOut,
    ZfinReagentOut,
    ZfinReagentSearchOut,
    ZfinWildtypeOut,
)
from zapp_atlas.api.services.zfin_lookup import ZfinDataUnavailable, ZfinIndex, get_index
from zapp_atlas.settings import AppSettings

router = APIRouter(prefix="/zfin", tags=["zfin"])

SettingsDep = Annotated[AppSettings, Depends(get_app_settings)]


def _index(settings: AppSettings) -> ZfinIndex:
    try:
        return get_index(settings.zfin_data_dir)
    except ZfinDataUnavailable as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/alleles", response_model=ZfinAlleleSearchOut)
def search_alleles_endpoint(
    settings: SettingsDep,
    q: Annotated[str, Query(min_length=1, max_length=100)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ZfinAlleleSearchOut:
    index = _index(settings)
    total, records = index.search_alleles(q, limit)
    return ZfinAlleleSearchOut(
        query=q,
        total_matches=total,
        indexed_alleles=index.allele_count,
        results=[ZfinAlleleOut.model_validate(r) for r in records],
    )


@router.get("/reagents", response_model=ZfinReagentSearchOut)
def search_reagents_endpoint(
    settings: SettingsDep,
    q: Annotated[str, Query(min_length=1, max_length=100)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ZfinReagentSearchOut:
    index = _index(settings)
    total, records = index.search_reagents(q, limit)
    return ZfinReagentSearchOut(
        query=q,
        total_matches=total,
        indexed_reagents=index.reagent_count,
        results=[ZfinReagentOut.model_validate(r) for r in records],
    )


@router.get("/wildtypes", response_model=list[ZfinWildtypeOut])
def list_wildtypes_endpoint(settings: SettingsDep) -> list[ZfinWildtypeOut]:
    return [ZfinWildtypeOut.model_validate(w) for w in _index(settings).wildtypes]
