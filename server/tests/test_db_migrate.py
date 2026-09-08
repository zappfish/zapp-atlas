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


# --- the fish re-key ---------------------------------------------------------

AB_FISH_ID = "ZFIN:ZDB-FISH-150901-27842"
# What the pre-re-key seed actually stored in Fish.zfin_id: AB's *genotype*
# id. The legacy slot took any ZDB type, so the rebuild routes by prefix.
AB_GENO_ID = "ZFIN:ZDB-GENO-960809-7"
STAMP = "2025-06-01 12:00:00.000000"


@pytest.fixture
def legacy_fish_db(tmp_path):
    """A database from before Fish was re-keyed, holding two lines in use.

    The legacy layout keyed ``Fish`` by ZFIN id and pointed ``FishTankEntry``
    and ``Experiment`` at that key — one line keyed the way the old seed did
    it (a genotype id in the fish slot) and one by an actual fish id. ``Fish``
    and ``FishTankEntry`` are recreated wholesale here; for ``Experiment``
    only the legacy column is restored (SQLite will not DROP a foreign-key
    column such as ``fish_id``), which still exercises the relink — a real
    legacy database gets ``fish_id`` from the generic column pass first.
    """
    path = tmp_path / "zapp.db"
    init_db(create_engine(f"sqlite:///{path}"))

    con = sqlite3.connect(path)
    con.executescript(
        f"""
        DROP TABLE "Fish";
        CREATE TABLE "Fish" (name TEXT NOT NULL, zfin_id TEXT NOT NULL PRIMARY KEY);
        DROP TABLE "FishTankEntry";
        CREATE TABLE "FishTankEntry" (
            research_group INTEGER NOT NULL REFERENCES "ResearchGroup" (id),
            id INTEGER NOT NULL PRIMARY KEY,
            fish_zfin_id TEXT NOT NULL REFERENCES "Fish" (zfin_id),
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        );
        ALTER TABLE "Experiment" ADD COLUMN fish_zfin_id TEXT REFERENCES "Fish" (zfin_id);

        INSERT INTO "Fish" (name, zfin_id) VALUES ('AB', '{AB_GENO_ID}');
        INSERT INTO "Fish" (name, zfin_id) VALUES ('AB by fish id', '{AB_FISH_ID}');
        INSERT INTO "ResearchGroup" (id, name) VALUES (1, 'Some Lab');
        INSERT INTO "FishTankEntry" (id, research_group, fish_zfin_id, created_at)
            VALUES (1, 1, '{AB_GENO_ID}', '{STAMP}');
        INSERT INTO "FishTankEntry" (id, research_group, fish_zfin_id)
            VALUES (2, 1, '{AB_FISH_ID}');
        INSERT INTO "Experiment" (id, fish_zfin_id) VALUES (1, '{AB_GENO_ID}');
        INSERT INTO "Experiment" (id, fish_zfin_id) VALUES (2, '{AB_FISH_ID}');
        """
    )
    con.commit()
    con.close()
    return path


def test_migrate_rebuilds_the_legacy_fish_table(legacy_fish_db) -> None:
    engine = create_engine(f"sqlite:///{legacy_fish_db}")

    migrate(engine)

    columns = {c["name"] for c in inspect(engine).get_columns("Fish")}
    assert "id" in columns and "zfin_id" not in columns and "name" not in columns
    with engine.connect() as connection:
        # Routed by prefix: the genotype-form id must NOT land in
        # fish_zfin_id, whose read pattern only accepts ZDB-FISH — copied
        # verbatim it would 500 every read of a seeded database.
        rows = connection.execute(text("SELECT fish_zfin_id, genotype_zfin_id FROM Fish")).all()
    assert set(rows) == {(None, AB_GENO_ID), (AB_FISH_ID, None)}


def test_migrate_rejoins_tank_entries_and_experiments(legacy_fish_db) -> None:
    engine = create_engine(f"sqlite:///{legacy_fish_db}")

    migrate(engine)

    with engine.connect() as connection:
        by_geno = connection.execute(
            text("SELECT id FROM Fish WHERE genotype_zfin_id = :g"), {"g": AB_GENO_ID}
        ).scalar()
        by_fish = connection.execute(
            text("SELECT id FROM Fish WHERE fish_zfin_id = :f"), {"f": AB_FISH_ID}
        ).scalar()
        linked = connection.execute(text("SELECT fish_id FROM FishTankEntry ORDER BY id")).scalars()
        assert list(linked) == [by_geno, by_fish]
        relinked = connection.execute(text("SELECT fish_id FROM Experiment ORDER BY id")).scalars()
        assert list(relinked) == [by_geno, by_fish]
        # The legacy tank timestamps rode along.
        stamp = connection.execute(
            text("SELECT created_at FROM FishTankEntry WHERE id = 1")
        ).scalar()
        assert stamp == STAMP


def test_the_rebuilt_fish_is_queryable_through_the_orm(legacy_fish_db) -> None:
    from sqlalchemy.orm import sessionmaker

    from zapp_atlas.api.dto import TankEntryOut
    from zapp_atlas.schema.sqla import FishTankEntry

    engine = create_engine(f"sqlite:///{legacy_fish_db}")
    migrate(engine)

    with sessionmaker(bind=engine)() as session:
        entry = session.get(FishTankEntry, 1)
        # The legacy fish's display name became the group's nickname.
        assert entry.nickname == "AB"
        # Serialization is where a mis-routed id would bite (pattern -> 500).
        out = TankEntryOut.model_validate(entry)
        assert out.fish.genotype_zfin_id == AB_GENO_ID
        assert out.fish.fish_zfin_id is None


def test_a_tank_entry_the_rebuild_cannot_carry_fails_loudly_and_changes_nothing(
    legacy_fish_db,
) -> None:
    """SQLite does not enforce the legacy FK, so an orphan entry is possible;
    dropping it silently would be data loss, so the rebuild refuses to start."""
    con = sqlite3.connect(legacy_fish_db)
    con.execute(
        "INSERT INTO FishTankEntry (id, research_group, fish_zfin_id)"
        " VALUES (3, 1, 'ZFIN:ZDB-FISH-000000-0')"
    )
    con.commit()
    con.close()
    engine = create_engine(f"sqlite:///{legacy_fish_db}")

    with pytest.raises(RuntimeError, match="tank entries"):
        migrate(engine)

    columns = {c["name"] for c in inspect(engine).get_columns("Fish")}
    assert "zfin_id" in columns  # still the untouched legacy layout


def test_the_fish_rebuild_is_idempotent(legacy_fish_db) -> None:
    engine = create_engine(f"sqlite:///{legacy_fish_db}")

    migrate(engine)
    migrate(engine)  # a second deploy of the same release

    with engine.connect() as connection:
        assert connection.execute(text("SELECT COUNT(*) FROM Fish")).scalar() == 2
        assert connection.execute(text("SELECT COUNT(*) FROM FishTankEntry")).scalar() == 2
