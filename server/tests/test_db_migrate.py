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


# Columns the nickname change (#113, #157) introduced. All optional, so the
# generic column step covers them. The unique keys on the nicknames are what
# needed the index step: create_all never adds an index to an existing table.
NICKNAME_ADDED = [
    ("Study", "research_group"),
    ("Study", "nickname"),
    ("Study", "description"),
    ("ChemicalCabinetEntry", "nickname"),
]
NICKNAME_INDEXES = {
    "Study": "uq_Study_study_nickname_grain",
    "ChemicalCabinetEntry": "uq_ChemicalCabinetEntry_cabinet_nickname_grain",
}


@pytest.fixture
def pre_nickname_db(tmp_path):
    """A database created before nicknames existed, holding two published studies.

    ``Study`` is recreated wholesale in its earlier layout: SQLite will not
    DROP a foreign-key column such as ``research_group``.
    """
    path = tmp_path / "zapp.db"
    init_db(create_engine(f"sqlite:///{path}"))

    con = sqlite3.connect(path)
    con.executescript(
        """
        DROP TABLE "Study";
        CREATE TABLE "Study" (publication TEXT, lab TEXT, id INTEGER NOT NULL PRIMARY KEY);
        DROP INDEX "uq_ChemicalCabinetEntry_cabinet_nickname_grain";
        ALTER TABLE "ChemicalCabinetEntry" DROP COLUMN "nickname";
        INSERT INTO "ResearchGroup" (id, name) VALUES (1, 'Some Lab');
        INSERT INTO "ChemicalCabinetEntry" (id, research_group, chemical_id)
            VALUES (1, 1, 'CHEBI:16236');
        """
    )
    con.execute("INSERT INTO Study (id, publication) VALUES (1, 'PMID:22194820')")
    con.execute("INSERT INTO Study (id, publication) VALUES (2, 'PMID:40359302')")
    con.commit()
    con.close()
    return path


def test_migrate_adds_the_nickname_columns(pre_nickname_db) -> None:
    from sqlalchemy.orm import sessionmaker

    from zapp_atlas.schema.sqla import ChemicalCabinetEntry, Study

    engine = create_engine(f"sqlite:///{pre_nickname_db}")

    migrate(engine)

    for table, column in NICKNAME_ADDED:
        assert column in {c["name"] for c in inspect(engine).get_columns(table)}
    with sessionmaker(bind=engine)() as session:
        study = session.get(Study, 1)
        assert study.publication == "PMID:22194820"
        # Existing rows are published, belong to no group, and have no nickname yet.
        assert study.research_group is None
        assert study.nickname is None
        assert study.description is None
        entry = session.get(ChemicalCabinetEntry, 1)
        assert entry.chemical_id == "CHEBI:16236"
        assert entry.nickname is None


def test_migrate_makes_nicknames_unique_within_a_group(pre_nickname_db) -> None:
    from sqlalchemy.exc import IntegrityError

    engine = create_engine(f"sqlite:///{pre_nickname_db}")

    migrate(engine)

    for table, name in NICKNAME_INDEXES.items():
        indexes = {i["name"]: i for i in inspect(engine).get_indexes(table)}
        assert indexes[name]["unique"]
        assert indexes[name]["column_names"] == ["research_group", "nickname"]

    named = "UPDATE Study SET research_group = 1, nickname = 'BPA pilot' WHERE id = :id"
    with engine.begin() as connection:
        connection.execute(text(named), {"id": 1})
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(text(named), {"id": 2})


def test_rows_that_break_a_new_key_are_reported_and_the_app_still_starts(
    pre_nickname_db, caplog
) -> None:
    engine = create_engine(f"sqlite:///{pre_nickname_db}")
    migrate(engine)  # adds the columns and both indexes
    name = NICKNAME_INDEXES["ChemicalCabinetEntry"]
    with engine.begin() as connection:
        connection.execute(text(f'DROP INDEX "{name}"'))
        connection.execute(text("UPDATE ChemicalCabinetEntry SET nickname = 'stock'"))
        connection.execute(
            text(
                "INSERT INTO ChemicalCabinetEntry (research_group, chemical_id, nickname) "
                "VALUES (1, 'CHEBI:33216', 'stock')"
            )
        )

    migrate(engine)

    assert name in caplog.text
    assert name not in {i["name"] for i in inspect(engine).get_indexes("ChemicalCabinetEntry")}
    # The key that could be added still was.
    assert NICKNAME_INDEXES["Study"] in {i["name"] for i in inspect(engine).get_indexes("Study")}


def test_migrate_is_a_no_op_on_a_fresh_database(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'fresh.db'}")
    init_db(engine)  # already runs migrate once

    migrate(engine)

    with engine.connect() as connection:
        assert connection.execute(text("SELECT COUNT(*) FROM StressorChemical")).scalar() == 0
