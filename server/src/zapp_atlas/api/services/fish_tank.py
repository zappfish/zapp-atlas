"""Fish tank persistence (a group's maintained fish lines).

A tank entry owns its whole Fish graph: fish are inlined per use, not shared
rows, because integer-keyed Fish has no natural key the database could dedupe
on (two labs' "AB" may differ in zygosity detail). The handle is the group's
own NICKNAME for the line — the thing the picker shows — so that is the
dedup key: ``add_entry`` answers 409 when the group already uses the nickname,
and the ``tank_grain`` unique index (research_group, nickname) backs it up.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from zapp_atlas.api.services.fish import fish_from_create
from zapp_atlas.schema.pydantic_crud import FishCreate
from zapp_atlas.schema.sqla import FishTankEntry  # type: ignore

_DUPLICATE = "That nickname is already used in this tank"


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


def _is_duplicate(session: Session, group_id: int, nickname: str) -> bool:
    return (
        session.query(FishTankEntry)
        .filter(
            FishTankEntry.research_group == group_id,
            FishTankEntry.nickname == nickname,
        )
        .first()
        is not None
    )


def add_entry(session: Session, group_id: int, nickname: str, payload: FishCreate) -> FishTankEntry:
    if _is_duplicate(session, group_id, nickname):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_DUPLICATE)
    entry = FishTankEntry(
        research_group=group_id, nickname=nickname, fish=fish_from_create(payload)
    )
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
