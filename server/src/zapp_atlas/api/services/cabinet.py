"""Chemical cabinet persistence (a group's on-hand chemicals).

An entry is one stock on the shelf, so the grain is ``(research_group,
chemical_id, manufacturer)``: the same chemical from two suppliers is two
entries, both pickable while a group transitions between suppliers. A
duplicate stock is a 409, backed by the ``cabinet_supplier_grain`` index —
except when neither entry names a supplier, which the index cannot see
(SQLite treats every NULL as distinct in a unique index) and a check here
catches instead.

An entry may carry the group's own nickname for the chemical. It is what the
picker lists the chemical under, so no two entries in a group may share one:
a reused nickname is a 409, backed by the ``cabinet_nickname_grain`` index.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from zapp_atlas.api.errors import SchemaRuleViolation
from zapp_atlas.api.persistence import commit_or_conflict
from zapp_atlas.api.rules import OTHER_NOT_LISTED, check_escape_hatch
from zapp_atlas.schema.pydantic_crud import ManufacturerEnum, VehicleEnum
from zapp_atlas.schema.sqla import ChemicalCabinetEntry

_CHEMICAL_TAKEN = "That chemical from the same supplier is already in this cabinet"
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


def _check_stock_is_free(
    session: Session,
    group_id: int,
    chemical_id: str,
    manufacturer: object,
    *,
    entry_id: int | None = None,
) -> None:
    """Catch the duplicate the supplier grain index cannot: no supplier twice."""
    if manufacturer is not None:
        return  # a named supplier is covered by the unique index
    query = session.query(ChemicalCabinetEntry).filter(
        ChemicalCabinetEntry.research_group == group_id,
        ChemicalCabinetEntry.chemical_id == chemical_id,
        ChemicalCabinetEntry.manufacturer.is_(None),
    )
    if entry_id is not None:
        query = query.filter(ChemicalCabinetEntry.id != entry_id)
    if query.first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_CHEMICAL_TAKEN)


def _check_vehicle_is_nameable(vehicle_type: object) -> None:
    """The entry's chemical-identity slots describe the stocked chemical, so
    there is nothing to name an unlisted vehicle with — the escape hatch that
    VehicleOfTransmission allows records no recoverable vehicle here."""
    if vehicle_type == OTHER_NOT_LISTED:
        raise SchemaRuleViolation(
            f"vehicle_type '{OTHER_NOT_LISTED}' is not accepted in the cabinet: "
            "a cabinet entry has no slot to name an unlisted vehicle."
        )


def _commit(session: Session) -> None:
    commit_or_conflict(session, _CHEMICAL_TAKEN, named={"nickname": _NICKNAME_TAKEN})


def add_entry(
    session: Session,
    group_id: int,
    chemical_id: str,
    *,
    nickname: str | None = None,
    manufacturer: ManufacturerEnum | None = None,
    unrecognized_manufacturer_name: str | None = None,
    vehicle_type: VehicleEnum | None = None,
) -> ChemicalCabinetEntry:
    _check_vehicle_is_nameable(vehicle_type)
    _check_nickname_is_free(session, group_id, nickname)
    _check_stock_is_free(session, group_id, chemical_id, manufacturer)
    entry = ChemicalCabinetEntry(
        research_group=group_id,
        chemical_id=chemical_id,
        nickname=nickname,
        manufacturer=manufacturer,
        unrecognized_manufacturer_name=unrecognized_manufacturer_name,
        vehicle_type=vehicle_type,
    )
    check_escape_hatch(entry, "manufacturer", "unrecognized_manufacturer_name", "manufacturer")
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
    manufacturer: ManufacturerEnum | None = None,
    unrecognized_manufacturer_name: str | None = None,
    vehicle_type: VehicleEnum | None = None,
) -> ChemicalCabinetEntry | None:
    entry = get_entry(session, group_id, entry_id)
    if entry is None:
        return None
    _check_vehicle_is_nameable(vehicle_type)
    # Checked before anything is changed: the checks read from the database,
    # which would first write out a half-made change to the entry.
    _check_nickname_is_free(session, group_id, nickname, entry_id=entry.id)
    _check_stock_is_free(
        session,
        group_id,
        chemical_id if chemical_id is not None else entry.chemical_id,
        manufacturer if manufacturer is not None else entry.manufacturer,
        entry_id=entry.id,
    )
    if chemical_id is not None:
        entry.chemical_id = chemical_id
    if nickname is not None:
        entry.nickname = nickname
    if manufacturer is not None:
        entry.manufacturer = manufacturer
    if unrecognized_manufacturer_name is not None:
        entry.unrecognized_manufacturer_name = unrecognized_manufacturer_name
    if vehicle_type is not None:
        entry.vehicle_type = vehicle_type
    # Checked on the changed row rather than the patch, so a patch that flips
    # manufacturer to other_not_listed still counts a name set earlier.
    check_escape_hatch(entry, "manufacturer", "unrecognized_manufacturer_name", "manufacturer")
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
