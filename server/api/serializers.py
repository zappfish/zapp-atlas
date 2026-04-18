"""ORM → Pydantic Read coercion.

The LinkML CRUD generator emits ``inlined: false`` class-ranged slots as
plain ``str`` fields (e.g. ``ExposureEventRead.route: Optional[str]``),
but the SQLAlchemy relationship on the same name returns an ORM instance.
Pydantic's ``from_attributes`` reads that instance and fails type-checking
because it isn't a string.

``OrmView`` wraps an ORM row (and any nested rows it exposes) so that
attribute lookups return CURIE strings for those specific fields while
passing everything else through. Router code calls
``StudyRead.model_validate(OrmView(study), from_attributes=True)`` and
gets a fully populated Pydantic model back.

This shim goes away when the generator learns to emit the right validator
itself (tracked as a follow-up on the schema repo).
"""

from __future__ import annotations

from typing import Any

from zebrafish_toxicology_atlas_schema.datamodel.sqla import (  # type: ignore
    ExposureEvent,
)


# ``(orm_class, attribute_name)`` pairs where the value should be flattened
# to its ``term_uri`` before handing it to Pydantic.
_COERCE_TO_TERM_URI: set[tuple[type, str]] = {
    (ExposureEvent, "route"),
    (ExposureEvent, "exposure_type"),
}


def _is_orm(value: Any) -> bool:
    return hasattr(value, "__table__")


class OrmView:
    """Wrap an ORM row so nested rows also come back wrapped, and the
    specific ``(class, attr)`` pairs above resolve to their ``term_uri``."""

    __slots__ = ("_obj",)

    def __init__(self, obj: Any) -> None:
        self._obj = obj

    def __getattr__(self, name: str) -> Any:
        value = getattr(self._obj, name)

        if (type(self._obj), name) in _COERCE_TO_TERM_URI:
            return getattr(value, "term_uri", None) if value is not None else None

        if isinstance(value, list):
            return [OrmView(v) if _is_orm(v) else v for v in value]

        if _is_orm(value):
            return OrmView(value)

        return value
