"""ZFIN autocomplete proxy + curated wild-type list.

The client never talks to zfin.org directly — it goes through here to avoid
CORS hassles and to give us a stable shape.

ZFIN's quicksearch only returns results for ``category=Fish`` (specific
genotype-line records like AB+MO5, transgenics, etc.). It does NOT surface
the canonical wild-type genotype records (plain AB, TU, WIK, ...), even
though those records exist in ZFIN as ``ZDB-GENO-*`` IDs. For curators who
want a plain wild-type background we expose a small hand-maintained list.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx
from fastapi import APIRouter, HTTPException, Query, status


ZFIN_AUTOCOMPLETE_URL = "https://zfin.org/action/quicksearch/autocomplete"

router = APIRouter(prefix="/zfin", tags=["zfin"])


@dataclass(frozen=True)
class WildType:
    zfin_id: str
    name: str


# Curated, verified against ZFIN. All IDs resolve to "ZFIN Genotype: <name>".
# Extend as curators request additions.
WILD_TYPES: list[WildType] = [
    WildType(zfin_id="ZFIN:ZDB-GENO-960809-7", name="AB"),
    WildType(zfin_id="ZFIN:ZDB-GENO-990623-3", name="Tübingen"),
    WildType(zfin_id="ZFIN:ZDB-GENO-990623-2", name="Tüpfel long fin"),
    WildType(zfin_id="ZFIN:ZDB-GENO-010531-2", name="WIK"),
    WildType(zfin_id="ZFIN:ZDB-GENO-031202-1", name="AB/TL"),
]


@router.get("/wildtypes")
def wildtype_list(q: str | None = None) -> list[dict]:
    """Curated wild-type genotype list. Optional ``q`` case-insensitively
    filters names and ZFIN IDs."""
    ql = (q or "").strip().lower()
    results = WILD_TYPES
    if ql:
        results = [
            wt
            for wt in WILD_TYPES
            if ql in wt.name.lower() or ql in wt.zfin_id.lower()
        ]
    return [{"zfin_id": wt.zfin_id, "name": wt.name} for wt in results]


@router.get("/fish-autocomplete")
async def fish_autocomplete(q: str = Query(..., min_length=1)) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                ZFIN_AUTOCOMPLETE_URL,
                params={"category": "Fish", "q": q},
            )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"ZFIN upstream error: {exc}",
        ) from exc

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"ZFIN upstream returned {resp.status_code}",
        )

    try:
        return resp.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"ZFIN upstream returned non-JSON: {exc}",
        ) from exc
