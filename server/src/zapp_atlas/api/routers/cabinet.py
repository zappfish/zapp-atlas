"""Chemical cabinet endpoints (a research group's on-hand chemicals).

All endpoints are scoped to a group in the path and require membership. The
grain ``(research_group, chemical_id)`` is unique, so a duplicate POST is a
409. ``research_group`` is always taken from the path, never a request body.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from zapp_atlas.api.authz import GroupMember
from zapp_atlas.api.deps import get_session
from zapp_atlas.api.dto import CabinetEntryIn, CabinetEntryOut, CabinetEntryPatch
from zapp_atlas.api.services.cabinet import (
    add_entry,
    delete_entry,
    get_entry,
    list_entries,
    update_entry,
)

router = APIRouter(
    prefix="/research-groups/{group_id}/chemical-cabinet",
    tags=["chemical-cabinet"],
)

SessionDep = Annotated[Session, Depends(get_session)]

_NOT_FOUND = "Cabinet entry not found"


@router.get("", response_model=list[CabinetEntryOut])
def list_cabinet_endpoint(
    group_id: int,
    session: SessionDep,
    _: GroupMember,
    limit: int = 50,
    offset: int = 0,
) -> list[CabinetEntryOut]:
    rows = list_entries(session, group_id, limit=limit, offset=offset)
    return [CabinetEntryOut.model_validate(r) for r in rows]


@router.post("", response_model=CabinetEntryOut, status_code=status.HTTP_201_CREATED)
def add_cabinet_endpoint(
    group_id: int,
    payload: CabinetEntryIn,
    session: SessionDep,
    _: GroupMember,
) -> CabinetEntryOut:
    entry = add_entry(session, group_id, payload.chemical_id)
    return CabinetEntryOut.model_validate(entry)


@router.get("/{entry_id}", response_model=CabinetEntryOut)
def get_cabinet_endpoint(
    group_id: int,
    entry_id: int,
    session: SessionDep,
    _: GroupMember,
) -> CabinetEntryOut:
    entry = get_entry(session, group_id, entry_id)
    if entry is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND)
    return CabinetEntryOut.model_validate(entry)


@router.patch("/{entry_id}", response_model=CabinetEntryOut)
def patch_cabinet_endpoint(
    group_id: int,
    entry_id: int,
    patch: CabinetEntryPatch,
    session: SessionDep,
    _: GroupMember,
) -> CabinetEntryOut:
    entry = update_entry(session, group_id, entry_id, chemical_id=patch.chemical_id)
    if entry is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND)
    return CabinetEntryOut.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cabinet_endpoint(
    group_id: int,
    entry_id: int,
    session: SessionDep,
    _: GroupMember,
) -> None:
    if not delete_entry(session, group_id, entry_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND)
