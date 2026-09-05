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
    ``name, zfin_id TEXT PRIMARY KEY``; the new one is integer-keyed, with the
    ZFIN id demoted to an optional ``fish_zfin_id`` column beside the
    curator-entered description (alleles, background). SQLite cannot ADD a
    primary key to an existing table, so the table is renamed aside, recreated
    from the current models, and its rows copied over. The legacy copy is then
    dropped — unlike a kept column, a renamed table would not help a rollback
    find its data anyway.
    """
    inspector = inspect(engine)
    if "Fish" not in inspector.get_table_names():
        return
    if "zfin_id" not in _existing_columns(engine, "Fish"):
        return  # already the integer-keyed layout

    with engine.begin() as connection:
        connection.execute(text('ALTER TABLE "Fish" RENAME TO "Fish_legacy"'))
    Base.metadata.tables["Fish"].create(engine)
    with engine.begin() as connection:
        copied = connection.execute(
            text('INSERT INTO "Fish" (name, fish_zfin_id) SELECT name, zfin_id FROM "Fish_legacy"')
        ).rowcount
        connection.execute(text('DROP TABLE "Fish_legacy"'))
    log.info("rebuilt Fish from the legacy zfin_id-keyed layout (%s row(s))", copied)


def _rebuild_legacy_fish_tank(engine: Engine) -> None:
    """Point ``FishTankEntry`` at the rebuilt ``Fish`` rows.

    The legacy layout referenced fish by ZFIN id (``fish_zfin_id`` NOT NULL);
    the new column is the integer ``fish_id``, which cannot be added to a table
    with rows because it has no default. Rebuilt the same way as ``Fish``, with
    ``fish_id`` filled by joining the ZFIN id each entry used to hold. Must run
    after :func:`_rebuild_legacy_fish`, which populates the join target.
    """
    inspector = inspect(engine)
    if "FishTankEntry" not in inspector.get_table_names():
        return
    if "fish_zfin_id" not in _existing_columns(engine, "FishTankEntry"):
        return

    with engine.begin() as connection:
        connection.execute(text('ALTER TABLE "FishTankEntry" RENAME TO "FishTankEntry_legacy"'))
    Base.metadata.tables["FishTankEntry"].create(engine)
    with engine.begin() as connection:
        copied = connection.execute(
            text(
                """
                INSERT INTO "FishTankEntry" (id, research_group, fish_id)
                SELECT entry.id, entry.research_group, fish.id
                FROM "FishTankEntry_legacy" AS entry
                JOIN "Fish" AS fish ON fish.fish_zfin_id = entry.fish_zfin_id
                """
            )
        ).rowcount
        connection.execute(text('DROP TABLE "FishTankEntry_legacy"'))
    log.info("rebuilt FishTankEntry against the rebuilt Fish rows (%s row(s))", copied)


def _relink_experiments_to_fish(engine: Engine) -> None:
    """Fill ``Experiment.fish_id`` from the legacy ``fish_zfin_id`` column.

    Legacy experiments referenced their fish by ZFIN id; ``fish_id`` is added
    generically (it is nullable) and filled here from the id the row used to
    hold. The old column stays in place, matching the chemical migration's
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
                    WHERE "Fish".fish_zfin_id = "Experiment".fish_zfin_id
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

    The fish rebuilds run before the generic column pass: until they have run,
    a legacy database is missing ``Fish.id`` and ``FishTankEntry.fish_id`` —
    primary key and NOT NULL respectively, which ``_add_missing_columns``
    refuses rather than half-applies.
    """
    _rebuild_legacy_fish(engine)
    _rebuild_legacy_fish_tank(engine)
    _add_missing_columns(engine)
    _relink_experiments_to_fish(engine)
    _move_chemical_names_into_synonyms(engine)
    _rename_vehicle_types(engine)
