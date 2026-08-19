"""Constraints the LinkML generator cannot yet emit.

``gen-sqla`` renders neither ``unique_keys`` nor timestamp defaults. Both are
read back out of the schema and attached to the generated tables, so the YAML
stays the single source of truth. Delete this module once the generator
supports them.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from linkml_runtime import SchemaView
from linkml_runtime.linkml_model.meta import ClassDefinition
from sqlalchemy import Column, DateTime, Index, Table

from zapp_atlas.schema._gen.sqla import Base

SCHEMA_PATH = Path(__file__).resolve().parent / "zebrafish_toxicology_atlas_schema.yaml"

TIMESTAMPED = "timestamped"


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _column(view: SchemaView, table: Table, class_name: str, slot_name: str) -> Column:
    """Resolve a LinkML slot to the column ``gen-sqla`` generated for it.

    An inlined slot whose range carries an identifier becomes
    ``<slot>_<identifier>`` (``fish`` -> ``fish_zfin_id``); every other slot
    keeps its own name.
    """
    if slot_name in table.c:
        return table.c[slot_name]

    identifier = view.get_identifier_slot(view.induced_slot(slot_name, class_name).range)
    if identifier is not None:
        qualified = f"{slot_name}_{identifier.name}"
        if qualified in table.c:
            return table.c[qualified]

    raise KeyError(f"{class_name}.{slot_name} has no generated column")


def _apply_unique_keys(view: SchemaView, model: type, definition: ClassDefinition) -> None:
    table = model.__table__
    existing = {index.name for index in table.indexes}
    for key_name, key in definition.unique_keys.items():
        name = f"uq_{definition.name}_{key_name}"
        if name in existing:
            continue
        columns = [_column(view, table, definition.name, s) for s in key.unique_key_slots]
        Index(name, *columns, unique=True)


def _apply_timestamps(model: type) -> None:
    if "created_at" in model.__table__.c:
        return
    # Set on the class rather than the table: declarative has already mapped
    # this model, and only attribute assignment also reaches the mapper.
    model.created_at = Column(DateTime(timezone=True), default=_utcnow)
    model.updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


def apply_schema_constraints(schema_path: Path = SCHEMA_PATH) -> None:
    """Attach every schema-declared unique key and timestamp pair. Idempotent."""
    view = SchemaView(str(schema_path))
    models = {mapper.class_.__name__: mapper.class_ for mapper in Base.registry.mappers}
    for class_name, definition in view.all_classes().items():
        model = models.get(class_name)
        if model is None:
            continue
        _apply_unique_keys(view, model, definition)
        if TIMESTAMPED in definition.annotations:
            _apply_timestamps(model)
