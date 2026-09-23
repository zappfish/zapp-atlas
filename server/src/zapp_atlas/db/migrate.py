"""Bring an existing database up to the current schema.

``create_all`` creates tables that are missing but never alters one that
already exists, so a database on a persistent disk keeps whatever columns it
was first created with. Deploying a schema change onto it leaves the code
asking for columns the file does not have, and every query touching that table
fails with ``no such column``.

This module closes that gap for the databases we actually have: it adds
columns that appeared since the file was created, and applies the handful of
data moves that a column rename implies. Everything here is idempotent and a
no-op on a database that is already current -- including a fresh one, which is
why tests exercise it on every run.

It is deliberately not a migration framework. There is no version table and no
down-grade path; each data fix carries its own "has this already happened?"
check. If schema changes become frequent enough that these accumulate, that is
the signal to adopt Alembic rather than to keep extending this.
"""

from __future__ import annotations

import logging

from sqlalchemy import Engine, inspect, text
from sqlalchemy.schema import CreateColumn

from zapp_atlas.schema.sqla import Base

log = logging.getLogger(__name__)

# Vehicle values renamed in the chemical data-model update: the enum member
# `albumin_bsa` became `bsa`. Stored rows still hold the old string, which no
# longer resolves to a member and raises LookupError on read.
RENAMED_VEHICLE_TYPES = {"albumin_bsa": "bsa"}


def _existing_columns(engine: Engine, table: str) -> set[str]:
    return {column["name"] for column in inspect(engine).get_columns(table)}


def _add_missing_columns(engine: Engine) -> None:
    """Add every column the models declare that the database does not have.

    Generic rather than a list of names, so the next schema change that only
    adds optional columns needs nothing here. A missing column that is NOT NULL
    without a default cannot be added to a table that already has rows, so that
    is reported rather than half-applied.
    """
    inspector = inspect(engine)
    present_tables = set(inspector.get_table_names())

    for table in Base.metadata.sorted_tables:
        if table.name not in present_tables:
            continue  # create_all will have made it in full
        existing = _existing_columns(engine, table.name)
        for column in table.columns:
            if column.name in existing:
                continue
            if not column.nullable and column.default is None and column.server_default is None:
                raise RuntimeError(
                    f"{table.name}.{column.name} is required but missing from the database, "
                    "and cannot be added without a default. It needs a hand-written fix."
                )
            spec = CreateColumn(column).compile(engine).string
            with engine.begin() as connection:
                connection.execute(text(f'ALTER TABLE "{table.name}" ADD COLUMN {spec}'))
            log.info("added column %s.%s", table.name, column.name)


def _rebuild_legacy_fish(engine: Engine) -> None:
    """Rebuild ``Fish`` from the layout that keyed fish by ZFIN id.

    The fish data-model change re-keyed the table: the old layout was
    ``name, zfin_id TEXT PRIMARY KEY``; the new one is integer-keyed, with
    optional ``fish_zfin_id`` / ``genotype_zfin_id`` columns beside the
    curator-entered description (alleles, background). SQLite cannot ADD a
    primary key to an existing table, so the table is renamed aside, recreated
    from the current models, and its rows copied over. Data that the copy
    could not carry stops the rebuild BEFORE anything is renamed: the sqlite3
    driver autocommits DDL, so a failure midway could not back the renames
    out.

    The legacy ``zfin_id`` slot accepted any ZDB type, and the old seed itself
    stored AB's *genotype* id in it — so the copy routes each value by prefix:
    ZDB-FISH ids land in ``fish_zfin_id``, ZDB-GENO ids in
    ``genotype_zfin_id``. The read models enforce exactly those shapes;
    copying verbatim would 500 every read of a seeded database. Any other
    prefix has no column that will take it and is logged instead.
    """
    inspector = inspect(engine)
    if "Fish" not in inspector.get_table_names():
        return
    if "zfin_id" not in _existing_columns(engine, "Fish"):
        return  # already the integer-keyed layout

    rebuild_tank = "fish_zfin_id" in _existing_columns(engine, "FishTankEntry")
    # A real legacy database has the timestamp columns constraints.py
    # attaches; carry their values over when they are there to carry.
    stamps = [
        column
        for column in ("created_at", "updated_at")
        if rebuild_tank and column in _existing_columns(engine, "FishTankEntry")
    ]

    with engine.begin() as connection:
        unroutable = (
            connection.execute(
                text(
                    """
                    SELECT zfin_id FROM "Fish"
                    WHERE zfin_id NOT LIKE 'ZFIN:ZDB-FISH-%'
                      AND zfin_id NOT LIKE 'ZFIN:ZDB-GENO-%'
                    """
                )
            )
            .scalars()
            .all()
        )

        if rebuild_tank:
            # An entry whose fish row is missing (SQLite never enforced the
            # legacy FK) or whose id shape neither new column accepts would
            # silently fall out of the copy's joins — data loss. Refuse up
            # front instead, while the legacy layout is still untouched.
            uncarriable = connection.execute(
                text(
                    """
                    SELECT COUNT(*) FROM "FishTankEntry" AS entry
                    WHERE NOT EXISTS (
                        SELECT 1 FROM "Fish" AS legacy
                        WHERE legacy.zfin_id = entry.fish_zfin_id
                          AND (legacy.zfin_id LIKE 'ZFIN:ZDB-FISH-%'
                               OR legacy.zfin_id LIKE 'ZFIN:ZDB-GENO-%')
                    )
                    """
                )
            ).scalar()
            if uncarriable:
                raise RuntimeError(
                    f"{uncarriable} tank entries reference a missing fish row or a "
                    "ZFIN id shape neither new column accepts; the fish re-key "
                    "cannot carry them. Nothing was changed — this needs a hand fix."
                )

        connection.execute(text('ALTER TABLE "Fish" RENAME TO "Fish_legacy"'))
        Base.metadata.tables["Fish"].create(connection)
        # The legacy display name is not copied — Fish has no name column any
        # more (display strings are derived). Its one afterlife is below: it
        # becomes the tank entry's nickname.
        copied = connection.execute(
            text(
                """
                INSERT INTO "Fish" (fish_zfin_id, genotype_zfin_id)
                SELECT
                    CASE WHEN zfin_id LIKE 'ZFIN:ZDB-FISH-%' THEN zfin_id END,
                    CASE WHEN zfin_id LIKE 'ZFIN:ZDB-GENO-%' THEN zfin_id END
                FROM "Fish_legacy"
                """
            )
        ).rowcount

        # FishTankEntry changed in the same release: it referenced fish by
        # ZFIN id (fish_zfin_id NOT NULL) and had no nickname. Both
        # replacement columns are NOT NULL, so the table is rebuilt too —
        # fish_id by joining the ZFIN id each entry used to hold (in
        # whichever column it was routed to), nickname from the legacy fish's
        # display name (what the group called the line is exactly what the
        # column now means).
        entries = 0
        if rebuild_tank:
            connection.execute(text('ALTER TABLE "FishTankEntry" RENAME TO "FishTankEntry_legacy"'))
            Base.metadata.tables["FishTankEntry"].create(connection)
            stamp_cols = "".join(f", {column}" for column in stamps)
            stamp_vals = "".join(f", entry.{column}" for column in stamps)
            entries = connection.execute(
                text(
                    f"""
                    INSERT INTO "FishTankEntry"
                        (id, research_group, fish_id, nickname{stamp_cols})
                    SELECT entry.id, entry.research_group, fish.id, legacy.name{stamp_vals}
                    FROM "FishTankEntry_legacy" AS entry
                    JOIN "Fish_legacy" AS legacy ON legacy.zfin_id = entry.fish_zfin_id
                    JOIN "Fish" AS fish
                        ON entry.fish_zfin_id IN (fish.fish_zfin_id, fish.genotype_zfin_id)
                    """
                )
            ).rowcount
            connection.execute(text('DROP TABLE "FishTankEntry_legacy"'))

        connection.execute(text('DROP TABLE "Fish_legacy"'))

    if unroutable:
        log.warning(
            "legacy Fish id(s) neither ZDB-FISH nor ZDB-GENO form, left unmapped: %s",
            ", ".join(unroutable),
        )
    log.info("rebuilt Fish from the legacy zfin_id-keyed layout (%s row(s))", copied)
    if rebuild_tank:
        log.info("rebuilt FishTankEntry; legacy fish names became nicknames (%s row(s))", entries)


def _relink_experiments_to_fish(engine: Engine) -> None:
    """Fill ``Experiment.fish_id`` from the legacy ``fish_zfin_id`` column.

    Legacy experiments referenced their fish by ZFIN id; ``fish_id`` is added
    generically (it is nullable) and filled here from the id the row used to
    hold — matching either column the rebuild routed that id into. The old
    column stays in place, matching the chemical migration's
    keep-for-rollback precedent. MIN() keeps the fill deterministic even after
    the API starts inlining one Fish row per use.
    """
    columns = _existing_columns(engine, "Experiment")
    if not {"fish_id", "fish_zfin_id"} <= columns:
        return  # never legacy, or created after the re-key

    with engine.begin() as connection:
        relinked = connection.execute(
            text(
                """
                UPDATE "Experiment" SET fish_id = (
                    SELECT MIN(id) FROM "Fish"
                    WHERE "Experiment".fish_zfin_id
                        IN ("Fish".fish_zfin_id, "Fish".genotype_zfin_id)
                )
                WHERE fish_id IS NULL AND fish_zfin_id IS NOT NULL
                """
            )
        ).rowcount
    if relinked:
        log.info("relinked %s experiment(s) to their rebuilt Fish row", relinked)


def _move_chemical_names_into_synonyms(engine: Engine) -> None:
    """Carry the dropped ``chemical_name`` column over to ``synonym``.

    ``chemical_name`` held one human-readable name; ``synonym`` holds the list
    that replaced it. The old column is left in place -- SQLite can drop a
    column, but keeping it costs nothing and means a rollback to the previous
    release still finds its data.
    """
    if "StressorChemical" not in inspect(engine).get_table_names():
        return
    if "chemical_name" not in _existing_columns(engine, "StressorChemical"):
        return  # already migrated, or created after the rename

    with engine.begin() as connection:
        moved = connection.execute(
            text(
                """
                INSERT OR IGNORE INTO StressorChemical_synonym (StressorChemical_id, synonym)
                SELECT id, chemical_name FROM StressorChemical
                WHERE chemical_name IS NOT NULL AND chemical_name != ''
                """
            )
        ).rowcount
    if moved:
        log.info("moved %s chemical_name value(s) into StressorChemical_synonym", moved)


def _rename_vehicle_types(engine: Engine) -> None:
    """Rewrite stored vehicle values whose enum member was renamed."""
    if "VehicleOfTransmission" not in inspect(engine).get_table_names():
        return

    for old, new in RENAMED_VEHICLE_TYPES.items():
        with engine.begin() as connection:
            renamed = connection.execute(
                text(
                    "UPDATE VehicleOfTransmission SET vehicle_type = :new WHERE vehicle_type = :old"
                ),
                {"old": old, "new": new},
            ).rowcount
        if renamed:
            log.info("renamed %s vehicle_type row(s) from %s to %s", renamed, old, new)


def migrate(engine: Engine) -> None:
    """Apply every outstanding fix. Idempotent; safe on an up-to-date database.

    The fish rebuild runs before the generic column pass: until it has run,
    a legacy database is missing ``Fish.id`` and ``FishTankEntry.fish_id`` —
    primary key and NOT NULL respectively, which ``_add_missing_columns``
    refuses rather than half-applies.
    """
    _rebuild_legacy_fish(engine)
    _add_missing_columns(engine)
    _relink_experiments_to_fish(engine)
    _move_chemical_names_into_synonyms(engine)
    _rename_vehicle_types(engine)
