"""The schema's ``unique_keys`` and timestamp annotations reach the database.

``gen-sqla`` emits neither, so ``schema.constraints`` supplies them from the
YAML. These tests lock in that the grain of each join table is actually
enforced rather than merely declared.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from zapp_atlas.db.db import init_db
from zapp_atlas.schema.sqla import (
    ChemicalCabinetEntry,
    Fish,
    FishTankEntry,
    ResearchGroup,
    ResearchGroupMember,
)

ORCID = "ORCID:0000-0002-1825-0097"
ETHANOL = "CHEBI:16236"
AB_LINE = "ZFIN:ZDB-GENO-960809-7"


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    init_db(engine)
    with sessionmaker(bind=engine)() as session:
        yield session


@pytest.fixture
def group(session: Session) -> ResearchGroup:
    group = ResearchGroup(name="Test Lab")
    session.add(group)
    session.commit()
    return group


def assert_second_insert_rejected(session: Session, row: Callable[[], object]) -> None:
    """``row()`` must commit once and then violate the unique index."""
    session.add(row())
    session.commit()
    session.add(row())
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_cabinet_grain_is_unique_per_group_and_chemical(session, group):
    assert_second_insert_rejected(
        session,
        lambda: ChemicalCabinetEntry(research_group=group.id, chemical_id=ETHANOL),
    )


def test_tank_grain_is_unique_per_group_and_fish(session, group):
    session.add(Fish(zfin_id=AB_LINE, name="AB"))
    session.commit()
    assert_second_insert_rejected(
        session,
        lambda: FishTankEntry(research_group=group.id, fish_zfin_id=AB_LINE),
    )


def test_membership_grain_is_unique_per_group_and_member(session, group):
    assert_second_insert_rejected(
        session,
        lambda: ResearchGroupMember(research_group=group.id, member=ORCID, role="admin"),
    )


def test_two_groups_may_stock_the_same_chemical(session):
    groups = [ResearchGroup(name="Lab A"), ResearchGroup(name="Lab B")]
    session.add_all(groups)
    session.commit()

    session.add_all(ChemicalCabinetEntry(research_group=g.id, chemical_id=ETHANOL) for g in groups)
    session.commit()

    assert session.query(ChemicalCabinetEntry).count() == 2


def test_annotated_classes_get_audit_timestamps(session, group):
    entry = ChemicalCabinetEntry(research_group=group.id, chemical_id=ETHANOL)
    session.add(entry)
    session.commit()

    assert entry.created_at is not None
    assert entry.updated_at is not None
