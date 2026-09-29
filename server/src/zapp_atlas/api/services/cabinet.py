"""Chemical cabinet persistence (a group's on-hand chemicals).

An entry may carry the group's own nickname for the chemical. It is what the
picker lists the chemical under, so no two entries in a group may share one:
a reused nickname is a 409, backed by the ``cabinet_nickname_grain`` index.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from zapp_atlas.api.persistence import commit_or_conflict
from zapp_atlas.schema.sqla import ChemicalCabinetEntry

_CHEMICAL_TAKEN = "That chemical is already in this cabinet"
_NICKNAME_TAKEN = "That nickname is already used in this cabinet"


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


def _check_nickname_is_free(
    session: Session, group_id: int, nickname: str | None, *, entry_id: int | None = None
) -> None:
    if nickname is None:
        return
    query = session.query(ChemicalCabinetEntry).filter(
        ChemicalCabinetEntry.research_group == group_id,
        ChemicalCabinetEntry.nickname == nickname,
    )
    if entry_id is not None:
        query = query.filter(ChemicalCabinetEntry.id != entry_id)
    if query.first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_NICKNAME_TAKEN)


def _commit(session: Session) -> None:
    commit_or_conflict(session, _CHEMICAL_TAKEN, named={"nickname": _NICKNAME_TAKEN})


def add_entry(
    session: Session, group_id: int, chemical_id: str, *, nickname: str | None = None
) -> ChemicalCabinetEntry:
    _check_nickname_is_free(session, group_id, nickname)
    entry = ChemicalCabinetEntry(
        research_group=group_id, chemical_id=chemical_id, nickname=nickname
    )
    session.add(entry)
    _commit(session)
    session.refresh(entry)
    return entry


def update_entry(
    session: Session,
    group_id: int,
    entry_id: int,
    *,
    chemical_id: str | None,
    nickname: str | None = None,
) -> ChemicalCabinetEntry | None:
    entry = get_entry(session, group_id, entry_id)
    if entry is None:
        return None
    # Checked before anything is changed: the check reads from the database,
    # which would first write out a half-made change to the entry.
    _check_nickname_is_free(session, group_id, nickname, entry_id=entry.id)
    if chemical_id is not None:
        entry.chemical_id = chemical_id
    if nickname is not None:
        entry.nickname = nickname
    _commit(session)
    session.refresh(entry)
    return entry


def delete_entry(session: Session, group_id: int, entry_id: int) -> bool:
    entry = get_entry(session, group_id, entry_id)
    if entry is None:
        return False
    session.delete(entry)
    session.commit()
    return True
