"""Where the LinkML schema lives, and one shared view of it."""

from functools import cache
from pathlib import Path

from linkml_runtime import SchemaView

SCHEMA_PATH = Path(__file__).resolve().parent / "zebrafish_toxicology_atlas_schema.yaml"


@cache
def schema_view() -> SchemaView:
    return SchemaView(str(SCHEMA_PATH))


# Classes whose rows are shared reference data, looked up by a natural
# identifier, descend from this.
REFERENCE_BASES = ("OntologyEntity",)


def column_name(view: SchemaView, class_name: str, slot_name: str) -> str:
    """The column ``gen-sqla`` keeps a slot in.

    A slot whose range is another class is kept as that class's identifier, in
    ``<slot>_<identifier>`` (``research_group`` -> ``research_group_id``), and
    the slot's own name goes to a relationship. Any other slot keeps its name.
    """
    range_name = view.induced_slot(slot_name, class_name).range
    if range_name not in view.all_classes():
        return slot_name
    return f"{slot_name}_{view.get_identifier_slot(range_name).name}"


def is_reference(view: SchemaView, class_name: str) -> bool:
    """Is this a class of shared rows, as opposed to rows their parent owns?"""
    return any(base in view.class_ancestors(class_name) for base in REFERENCE_BASES)


@cache
def value_for_meaning(enum_name: str, curie: str | None) -> str | None:
    """The permissible value of an enum whose ``meaning`` is ``curie``, if any.

    How an ontology term in reference data (a ZFIN allele's SO type) becomes
    one of the schema's own values: the mapping is the enum's meanings in the
    YAML, so a value added there is understood here without a Python edit.
    """
    if curie is None:
        return None
    for name, value in schema_view().get_enum(enum_name).permissible_values.items():
        if value.meaning == curie:
            return name
    return None


def owned_slots(view: SchemaView, class_name: str) -> list[str]:
    """The slots of a class holding inlined objects that exist only as part of it."""
    return [
        slot.name
        for slot in view.class_induced_slots(class_name)
        if slot.inlined and slot.range in view.all_classes() and not is_reference(view, slot.range)
    ]
