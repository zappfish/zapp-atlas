"""ZFIN autocomplete proxy.

The client never talks to zfin.org directly — it goes through here to avoid
CORS hassles and to give us a stable shape.
"""

from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException, Query, status


ZFIN_AUTOCOMPLETE_URL = "https://zfin.org/action/quicksearch/autocomplete"

router = APIRouter(prefix="/zfin", tags=["zfin"])


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
