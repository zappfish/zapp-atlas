"""Fish tank persistence (a group's maintained fish lines)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from zapp_atlas.api.dto import FishRef
from zapp_atlas.api.persistence import commit_or_conflict
from zapp_atlas.schema.sqla import Fish, FishTankEntry


def _get_or_create_fish(session: Session, ref: FishRef) -> Fish:
    """Fish is a shared, ZFIN-keyed entity; reuse the row if it exists.

    When the row already exists its stored ``name`` wins — a payload ``name``
    is not written back, so the response echoes the canonical name rather than
    the submitted one. Names are a property of the shared Fish, not the tank
    entry.
    """
    fish = session.get(Fish, ref.zfin_id)
    if fish is None:
        fish = Fish(zfin_id=ref.zfin_id, name=ref.name)
        session.add(fish)
        session.flush()
    return fish


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


def add_entry(session: Session, group_id: int, fish: FishRef) -> FishTankEntry:
    row = _get_or_create_fish(session, fish)
    entry = FishTankEntry(research_group=group_id, fish_zfin_id=row.zfin_id)
    session.add(entry)
    commit_or_conflict(session, "That fish line is already in this tank")
    session.refresh(entry)
    return entry


def delete_entry(session: Session, group_id: int, entry_id: int) -> bool:
    entry = get_entry(session, group_id, entry_id)
    if entry is None:
        return False
    session.delete(entry)
    session.commit()
    return True
