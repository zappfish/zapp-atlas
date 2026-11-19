"""Checking the ontology terms a request names against the reference bundle.

A body says which term it means by its CURIE. Which ontology a slot draws
from is declared in the schema as ``id_prefixes``, on a slot that holds a
CURIE or on a class of shared term rows. A CURIE with another prefix is
refused, and so is one the bundle does not have, when the bundle carries that
ontology. A term's label is the bundle's, whatever the body says.

The bundle does not carry every ontology the schema names. A term from one
it lacks is held to its prefix alone, and keeps the label it was sent with.

Unlike the rest of ``api`` this names slots, since reading a term's id and
writing its label is about those two in particular.
"""

from pydantic import BaseModel
from sqlalchemy.orm import Session

from zapp_atlas.api.errors import SchemaRuleViolation
from zapp_atlas.api.layout import layout
from zapp_atlas.labels import Labels


class ReferenceDataMissing(RuntimeError):
    """labels.db is not installed, so no term can be checked."""


def checked(labels: Labels, prefixes: tuple[str, ...], curie: str) -> str | None:
    """The bundle's label for a term a slot may hold, or None when the bundle
    does not carry the term's ontology."""
    prefix = curie.partition(":")[0]
    if prefix not in prefixes:
        raise SchemaRuleViolation(f"{curie} is not a term from {' or '.join(prefixes)}.")
    if not labels.available:
        raise ReferenceDataMissing(
            "The reference data is not installed, so terms cannot be checked. "
            "Build the extdata bundle with `just extdata`."
        )
    if not labels.covers(prefix):
        return None
    label = labels.label(curie)
    if label is None:
        raise SchemaRuleViolation(f"{curie} is not a term {prefix} has.")
    return label


def term_values(session: Session, class_name: str, body: BaseModel) -> dict[str, object]:
    """What a shared term's row is stored with: what the body says, with the
    bundle's label in place of the body's when the bundle has the term."""
    values = body.model_dump()
    prefixes = tuple(layout().view.get_class(class_name).id_prefixes)
    if not prefixes:
        return values
    label = checked(session.info["labels"], prefixes, values["term_uri"])
    return values if label is None else values | {"term_label": label}
