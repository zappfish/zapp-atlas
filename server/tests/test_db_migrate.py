"""Upgrading a database that predates the chemical data-model change.

The deployed app keeps its database on a persistent disk, so a release lands
on a file created by an earlier one. ``create_all`` will not alter an existing
table, so these check that ``migrate`` does: the pre-change column layout has
to come out queryable, with its data carried over rather than stranded.
"""

from __future__ import annotations

import sqlite3

import pytest
from sqlalchemy import create_engine, inspect, text

from zapp_atlas.db import init_db
from zapp_atlas.db.migrate import migrate

# Columns the chemical data-model change introduced, dropped below to rebuild
# the layout a database created before it would have.
ADDED = [
    ("StressorChemical", "unrecognized_chemical_name"),
    ("StressorChemical", "unrecognized_manufacturer_name"),
    ("VehicleOfTransmission", "chemical_id"),
    ("VehicleOfTransmission", "cas_id"),
    ("VehicleOfTransmission", "unrecognized_chemical_name"),
    ("VehicleOfTransmission", "unrecognized_manufacturer_name"),
]


@pytest.fixture
def legacy_db(tmp_path):
    """A database with the column layout this change replaced, holding data."""
    path = tmp_path / "zapp.db"
    init_db(create_engine(f"sqlite:///{path}"))

    con = sqlite3.connect(path)
    for table, column in ADDED:
        con.execute(f'ALTER TABLE "{table}" DROP COLUMN "{column}"')
    con.execute('ALTER TABLE "StressorChemical" ADD COLUMN chemical_name TEXT')
    con.execute(
        "INSERT INTO StressorChemical (id, chemical_id, chemical_name) VALUES (1,'CHEBI:33216','bisphenol A')"
    )
    con.execute("INSERT INTO VehicleOfTransmission (id, vehicle_type) VALUES (1,'albumin_bsa')")
    con.commit()
    con.close()
    return path


def test_a_legacy_database_is_unqueryable_before_migrating(legacy_db) -> None:
    """The failure this exists to prevent, so the fixture can't drift into passing."""
    from sqlalchemy.exc import OperationalError
    from sqlalchemy.orm import sessionmaker

    from zapp_atlas.schema.sqla import StressorChemical

    engine = create_engine(f"sqlite:///{legacy_db}")
    with (
        sessionmaker(bind=engine)() as session,
        pytest.raises(OperationalError, match="no such column"),
    ):
        session.query(StressorChemical).all()


def test_migrate_adds_the_columns_and_keeps_the_rows(legacy_db) -> None:
    engine = create_engine(f"sqlite:///{legacy_db}")

    migrate(engine)

    for table, column in ADDED:
        assert column in {c["name"] for c in inspect(engine).get_columns(table)}
    with engine.connect() as connection:
        assert connection.execute(text("SELECT COUNT(*) FROM StressorChemical")).scalar() == 1


def test_migrate_carries_chemical_name_over_to_synonym(legacy_db) -> None:
    engine = create_engine(f"sqlite:///{legacy_db}")

    migrate(engine)

    with engine.connect() as connection:
        synonyms = connection.execute(
            text("SELECT synonym FROM StressorChemical_synonym WHERE StressorChemical_id = 1")
        ).scalars()
    assert list(synonyms) == ["bisphenol A"]


def test_migrate_renames_stored_vehicle_values(legacy_db) -> None:
    engine = create_engine(f"sqlite:///{legacy_db}")

    migrate(engine)

    with engine.connect() as connection:
        stored = connection.execute(
            text("SELECT vehicle_type FROM VehicleOfTransmission WHERE id = 1")
        ).scalar()
    assert stored == "bsa"


def test_the_migrated_database_is_queryable_through_the_orm(legacy_db) -> None:
    from sqlalchemy.orm import sessionmaker

    from zapp_atlas.schema.sqla import StressorChemical

    engine = create_engine(f"sqlite:///{legacy_db}")
    migrate(engine)

    with sessionmaker(bind=engine)() as session:
        stressor = session.get(StressorChemical, 1)
        assert stressor.chemical_id == "CHEBI:33216"
        assert list(stressor.synonym) == ["bisphenol A"]


def test_a_renamed_vehicle_value_can_be_served_again(legacy_db) -> None:
    """Where the stale value actually bites.

    SQLAlchemy hands back whatever string is stored, so the break does not show
    until the row is serialised: the read model's enum has no `albumin_bsa`
    member any more and rejects it, which is a 500 on an ordinary GET.
    """
    from pydantic import ValidationError
    from sqlalchemy.orm import sessionmaker

    from zapp_atlas.schema.pydantic_crud import VehicleOfTransmissionRead
    from zapp_atlas.schema.sqla import VehicleOfTransmission

    engine = create_engine(f"sqlite:///{legacy_db}")
    # Read the stored value with SQL: the ORM cannot load this table yet, which
    # is the separate breakage the column migration handles.
    with engine.connect() as connection:
        stale = connection.execute(
            text("SELECT vehicle_type FROM VehicleOfTransmission WHERE id = 1")
        ).scalar()
    with pytest.raises(ValidationError):
        VehicleOfTransmissionRead(id=1, vehicle_type=stale)

    migrate(engine)

    with sessionmaker(bind=engine)() as session:
        migrated = session.get(VehicleOfTransmission, 1).vehicle_type
    assert VehicleOfTransmissionRead(id=1, vehicle_type=migrated).vehicle_type == "bsa"


def test_migrate_is_idempotent(legacy_db) -> None:
    engine = create_engine(f"sqlite:///{legacy_db}")

    migrate(engine)
    migrate(engine)  # a second deploy of the same release

    with engine.connect() as connection:
        assert (
            connection.execute(text("SELECT COUNT(*) FROM StressorChemical_synonym")).scalar() == 1
        )


def test_migrate_is_a_no_op_on_a_fresh_database(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'fresh.db'}")
    init_db(engine)  # already runs migrate once

    migrate(engine)

    with engine.connect() as connection:
        assert connection.execute(text("SELECT COUNT(*) FROM StressorChemical")).scalar() == 0
