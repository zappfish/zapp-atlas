"""Fish tank persistence (a group's maintained fish lines).

A tank entry owns its whole Fish/Genotype graph: fish are inlined per use, not
shared rows, because integer-keyed Fish has no natural key the database could
dedupe on (two labs' "AB" may differ in cross or zygosity detail). The
``tank_grain`` unique index therefore no longer catches a duplicate line by
itself; ``add_entry`` checks the meaningful key instead — the ZFIN fish id when
the line has one, the name within the group when it does not — and answers 409.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from zapp_atlas.api.services.fish import fish_from_create
from zapp_atlas.schema.pydantic_crud import FishCreate
from zapp_atlas.schema.sqla import Fish, FishTankEntry  # type: ignore

_DUPLICATE = "That fish line is already in this tank"


def list_entries(
    session: Session, group_id: int, *, limit: int = 50, offset: int = 0
) -> list[FishTankEntry]:
    return (
        session.query(FishTankEntry)
        .filter(FishTankEntry.research_group == group_id)
        .order_by(FishTankEntry.id)
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_entry(session: Session, group_id: int, entry_id: int) -> FishTankEntry | None:
    # Scoped by group_id so a valid id under the wrong group reads as absent.
    return (
        session.query(FishTankEntry)
        .filter(
            FishTankEntry.id == entry_id,
            FishTankEntry.research_group == group_id,
        )
        .one_or_none()
    )


def _is_duplicate(session: Session, group_id: int, payload: FishCreate) -> bool:
    query = (
        session.query(FishTankEntry)
        .join(Fish, FishTankEntry.fish_id == Fish.id)
        .filter(FishTankEntry.research_group == group_id)
    )
    if payload.fish_zfin_id is not None:
        return query.filter(Fish.fish_zfin_id == payload.fish_zfin_id).first() is not None
    return query.filter(Fish.name == payload.name).first() is not None


def add_entry(session: Session, group_id: int, payload: FishCreate) -> FishTankEntry:
    if _is_duplicate(session, group_id, payload):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_DUPLICATE)
    entry = FishTankEntry(research_group=group_id, fish=fish_from_create(payload))
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


def delete_entry(session: Session, group_id: int, entry_id: int) -> bool:
    entry = get_entry(session, group_id, entry_id)
    if entry is None:
        return False
    session.delete(entry)
    session.commit()
    return True
