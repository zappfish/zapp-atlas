"""Fish tank persistence (a group's maintained fish lines).

An entry owns its Fish row, built by the same code that builds one inside an
experiment, and deleted with the entry. Two entries may describe the same
line. The nickname is unique within the group (``tank_nickname_grain``), so a
reused one is a 409.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from zapp_atlas.api import tree
from zapp_atlas.api.models import TankEntryIn
from zapp_atlas.api.persistence import commit_or_conflict
from zapp_atlas.schema.sqla import FishTankEntry

_NICKNAME_TAKEN = "That nickname is already used in this tank"


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


def add_entry(session: Session, group_id: int, payload: TankEntryIn) -> FishTankEntry:
    entry = FishTankEntry(
        research_group=group_id,
        nickname=payload.nickname,
        fish=tree.build(session, "Fish", payload.fish),
    )
    session.add(entry)
    commit_or_conflict(session, _NICKNAME_TAKEN)
    session.refresh(entry)
    return entry


def delete_entry(session: Session, group_id: int, entry_id: int) -> bool:
    entry = get_entry(session, group_id, entry_id)
    if entry is None:
        return False
    session.delete(entry)
    session.commit()
    return True
