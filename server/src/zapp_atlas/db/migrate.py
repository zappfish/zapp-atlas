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
    """Apply every outstanding fix. Idempotent; safe on an up-to-date database."""
    _add_missing_columns(engine)
    _move_chemical_names_into_synonyms(engine)
    _rename_vehicle_types(engine)
