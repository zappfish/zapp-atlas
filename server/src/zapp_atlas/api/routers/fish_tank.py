"""Fish tank endpoints (a research group's maintained fish lines).

Scoped to a group in the path and requires membership. A line already in the
group's tank (same ZFIN fish id, or same name for an unregistered line) is a
409. Each entry stores its own Fish/Genotype graph from the payload; malformed
ZFIN ids are rejected by the generated model's patterns (422).
``research_group`` is always path-derived.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from zapp_atlas.api.authz import GroupMember
from zapp_atlas.api.deps import get_session
from zapp_atlas.api.dto import TankEntryIn, TankEntryOut
from zapp_atlas.api.services.fish_tank import (
    add_entry,
    delete_entry,
    get_entry,
    list_entries,
)

router = APIRouter(
    prefix="/research-groups/{group_id}/fish-tank",
    tags=["fish-tank"],
)

SessionDep = Annotated[Session, Depends(get_session)]

_NOT_FOUND = "Tank entry not found"


@router.get("", response_model=list[TankEntryOut])
def list_tank_endpoint(
    group_id: int,
    session: SessionDep,
    _: GroupMember,
    limit: int = 50,
    offset: int = 0,
) -> list[TankEntryOut]:
    rows = list_entries(session, group_id, limit=limit, offset=offset)
    return [TankEntryOut.model_validate(r) for r in rows]


@router.post("", response_model=TankEntryOut, status_code=status.HTTP_201_CREATED)
def add_tank_endpoint(
    group_id: int,
    payload: TankEntryIn,
    session: SessionDep,
    _: GroupMember,
) -> TankEntryOut:
    entry = add_entry(session, group_id, payload.fish)
    return TankEntryOut.model_validate(entry)


@router.get("/{entry_id}", response_model=TankEntryOut)
def get_tank_endpoint(
    group_id: int,
    entry_id: int,
    session: SessionDep,
    _: GroupMember,
) -> TankEntryOut:
    entry = get_entry(session, group_id, entry_id)
    if entry is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND)
    return TankEntryOut.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tank_endpoint(
    group_id: int,
    entry_id: int,
    session: SessionDep,
    _: GroupMember,
) -> None:
    if not delete_entry(session, group_id, entry_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND)
