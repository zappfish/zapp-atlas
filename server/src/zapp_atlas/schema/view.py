"""Where the LinkML schema lives, and one shared view of it."""

from functools import cache
from pathlib import Path

from linkml_runtime import SchemaView

SCHEMA_PATH = Path(__file__).resolve().parent / "zebrafish_toxicology_atlas_schema.yaml"


@cache
def schema_view() -> SchemaView:
    return SchemaView(str(SCHEMA_PATH))


# Classes whose rows are shared reference data, looked up by a natural
# identifier, descend from one of these.
REFERENCE_BASES = ("OntologyEntity", "ZfinEntity")


def is_reference(view: SchemaView, class_name: str) -> bool:
    """Is this a class of shared rows, as opposed to rows their parent owns?"""
    return any(base in view.class_ancestors(class_name) for base in REFERENCE_BASES)


def owned_slots(view: SchemaView, class_name: str) -> list[str]:
    """The slots of a class holding inlined objects that exist only as part of it."""
    return [
        slot.name
        for slot in view.class_induced_slots(class_name)
        if slot.inlined and slot.range in view.all_classes() and not is_reference(view, slot.range)
    ]
