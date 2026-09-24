"""Chemical cabinet persistence (a group's on-hand chemicals)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from zapp_atlas.api.persistence import commit_or_conflict
from zapp_atlas.schema.sqla import ChemicalCabinetEntry


def list_entries(
    session: Session, group_id: int, *, limit: int = 50, offset: int = 0
) -> list[ChemicalCabinetEntry]:
    return (
        session.query(ChemicalCabinetEntry)
        .filter(ChemicalCabinetEntry.research_group == group_id)
        .order_by(ChemicalCabinetEntry.id)
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_entry(session: Session, group_id: int, entry_id: int) -> ChemicalCabinetEntry | None:
    # Scoped by group_id so a valid id under the wrong group reads as absent.
    return (
        session.query(ChemicalCabinetEntry)
        .filter(
            ChemicalCabinetEntry.id == entry_id,
            ChemicalCabinetEntry.research_group == group_id,
        )
        .one_or_none()
    )


def add_entry(session: Session, group_id: int, chemical_id: str) -> ChemicalCabinetEntry:
    entry = ChemicalCabinetEntry(research_group=group_id, chemical_id=chemical_id)
    session.add(entry)
    commit_or_conflict(session, "That chemical is already in this cabinet")
    session.refresh(entry)
    return entry


def update_entry(
    session: Session, group_id: int, entry_id: int, *, chemical_id: str | None
) -> ChemicalCabinetEntry | None:
    entry = get_entry(session, group_id, entry_id)
    if entry is None:
        return None
    if chemical_id is not None:
        entry.chemical_id = chemical_id
    commit_or_conflict(session, "That chemical is already in this cabinet")
    session.refresh(entry)
    return entry


def delete_entry(session: Session, group_id: int, entry_id: int) -> bool:
    entry = get_entry(session, group_id, entry_id)
    if entry is None:
        return False
    session.delete(entry)
    session.commit()
    return True
