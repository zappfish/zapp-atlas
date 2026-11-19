"""ZFIN reference lookups: the registry a described fish is matched against.

Public, read-only, and not group-scoped: this is ZFIN's data served back
from the extdata bundle (``zapp_atlas/zfin.py``), not anything a user wrote.

* ``GET /zfin/wildtypes`` -- the wild-type lines, for the background picker
* ``GET /zfin/alleles?q=`` -- allele autocomplete by symbol, gene or construct
* ``GET /zfin/alleles/{id}``, ``/genotypes/{id}``, ``/fish/{id}`` -- one
  record by CURIE, for showing a saved fish's ZFIN details again
* ``POST /zfin/resolve`` -- the registered genotype and fish a described fish
  (background, alleles with zygosity, injected reagents) corresponds to
* ``GET /zfin/status`` -- which ZFIN snapshot is installed, and how much of it

Responses carry ZFIN's own vocabulary (SO ids for alteration types, its
zygosity words, reagent kinds by id prefix) rather than the schema's enums,
so this surface does not move when the data model does.

503 means the bundle has no zfin.db; the detail says how to build it
(``zfin_unavailable_handler``, registered in ``create_app``).
"""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from zapp_atlas.api.models import (
    ZfinAlleleOut,
    ZfinAlleleSearchOut,
    ZfinFishOut,
    ZfinGenotypeOut,
    ZfinResolveIn,
    ZfinResolveOut,
    ZfinStatusOut,
    ZfinWildtypeOut,
)
from zapp_atlas.zfin import ZfinData, ZfinUnavailable

router = APIRouter(prefix="/zfin", tags=["zfin"])

_NOT_FOUND = "No ZFIN record with that id"


def zfin_unavailable_handler(request: Request, exc: ZfinUnavailable) -> JSONResponse:
    # A deployment without the bundle, not a bad request.
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"detail": str(exc)}
    )


@router.get("/status", response_model=ZfinStatusOut)
def status_endpoint(zfin: ZfinData) -> ZfinStatusOut:
    meta = zfin.meta()
    return ZfinStatusOut(
        zfin_date=meta["zfin_date"],
        counts={
            key.removesuffix("_count"): int(value)
            for key, value in meta.items()
            if key.endswith("_count")
        },
    )


@router.get("/wildtypes", response_model=list[ZfinWildtypeOut])
def wildtypes_endpoint(zfin: ZfinData) -> list[ZfinWildtypeOut]:
    return [ZfinWildtypeOut.model_validate(w) for w in zfin.wildtypes()]


@router.get("/alleles", response_model=ZfinAlleleSearchOut)
def search_alleles_endpoint(
    zfin: ZfinData,
    q: Annotated[str, Query(min_length=1, max_length=100)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ZfinAlleleSearchOut:
    total, alleles = zfin.search_alleles(q, limit)
    return ZfinAlleleSearchOut(
        query=q,
        total_matches=total,
        results=[ZfinAlleleOut.model_validate(a) for a in alleles],
    )


@router.get("/alleles/{allele_id}", response_model=ZfinAlleleOut)
def allele_endpoint(zfin: ZfinData, allele_id: str) -> ZfinAlleleOut:
    allele = zfin.allele(allele_id)
    if allele is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND)
    return ZfinAlleleOut.model_validate(allele)


@router.post("/resolve", response_model=ZfinResolveOut)
def resolve_endpoint(zfin: ZfinData, payload: ZfinResolveIn) -> ZfinResolveOut:
    resolution = zfin.resolve(
        alleles={a.allele_id: a.zygosity for a in payload.alleles},
        background_id=payload.background_id,
        reagents=set(payload.reagents),
    )
    return ZfinResolveOut.model_validate(resolution)


@router.get("/genotypes/{genotype_id}", response_model=ZfinGenotypeOut)
def genotype_endpoint(zfin: ZfinData, genotype_id: str) -> ZfinGenotypeOut:
    genotype = zfin.genotype(genotype_id)
    if genotype is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND)
    return ZfinGenotypeOut.model_validate(genotype)


@router.get("/fish/{fish_id}", response_model=ZfinFishOut)
def fish_endpoint(zfin: ZfinData, fish_id: str) -> ZfinFishOut:
    fish = zfin.fish(fish_id)
    if fish is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND)
    return ZfinFishOut.model_validate(fish)
