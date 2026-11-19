"""Saving any level of the study tree, driven by the layout.

Nothing here names a slot. ``assign`` walks the slots the layout says a class's
request body carries and stores each according to its kind, so a slot added to
the schema is persisted without a matching edit here. What a body does not
carry because the server works it out (``SlotKind.DERIVED``) is set by the
class's entry in ``_DERIVE``.
"""

from collections.abc import Callable, Iterator
from functools import partial

from linkml_runtime.linkml_model.meta import AnonymousClassExpression, PresenceEnum, SlotDefinition
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from zapp_atlas.api.errors import SchemaRuleViolation
from zapp_atlas.api.fish import set_zfin_ids
from zapp_atlas.api.layout import Slot, SlotKind, layout
from zapp_atlas.api.terms import checked, term_values
from zapp_atlas.schema import sqla
from zapp_atlas.schema.sqla import Base

# Sets a class's derived slots on a row, once the body has been stored on it.
_DERIVE: dict[str, Callable[[Session, Base], None]] = {"Fish": set_zfin_ids}


def build(session: Session, class_name: str, body: BaseModel) -> Base:
    """A new row for ``body``, with everything it owns."""
    row = getattr(sqla, class_name)()
    assign(session, class_name, row, body)
    return row


def assign(session: Session, class_name: str, row: Base, body: BaseModel) -> None:
    """Make ``row`` say what ``body`` says.

    Everything the row owned before is replaced, and the cascades declared in
    ``schema.constraints`` delete what is left behind. The next level down is
    not part of a body and is left alone.
    """
    for slot in layout().body_slots(class_name):
        setattr(row, slot.attribute, _stored(session, slot, getattr(body, slot.name)))
    _check_rules(class_name, row)
    if class_name in _DERIVE:
        _DERIVE[class_name](session, row)


def _stored(session: Session, slot: Slot, value: object) -> object:
    convert: Callable[[object], object]
    match slot.kind:
        case SlotKind.VALUE:
            convert = partial(_value, session, slot)
        case SlotKind.OWNED:
            convert = partial(build, session, slot.range)
        case SlotKind.REFERENCE:
            convert = partial(_shared, session, slot.range)
    if slot.multivalued:
        return [convert(item) for item in value or []]
    return None if value is None else convert(value)


def _value(session: Session, slot: Slot, value: object) -> object:
    """Blank text is no text at all, and a term is one its slot may hold."""
    if not isinstance(value, str):
        return value
    text = value.strip() or None
    if text is not None and slot.prefixes:
        checked(session.info["labels"], slot.prefixes, text)
    return text


def _shared(session: Session, class_name: str, body: BaseModel) -> Base:
    """The shared row ``body`` identifies, created from it if this is the first use."""
    model = getattr(sqla, class_name)
    identifier = layout().view.get_identifier_slot(class_name).name
    values = term_values(session, class_name, body)
    existing = session.scalars(
        select(model).where(getattr(model, identifier) == values[identifier])
    ).first()
    if existing is not None:
        # The row says what the bundle says now, whoever first named the term.
        for name, value in values.items():
            setattr(existing, name, value)
        return existing
    row = model(**values)
    # Added straight away so a second use in the same request finds this one.
    session.add(row)
    return row


def study_of(session: Session, level_name: str, row: Base) -> sqla.Study:
    """The study a row sits in, however many levels down it is."""
    level = layout().levels[level_name]
    while level.parent is not None:
        # ``gen-sqla`` names a child's foreign key after its parent's class.
        parent_id = getattr(row, f"{level.parent.name}_id")
        row = session.get_one(getattr(sqla, level.parent.name), parent_id)
        level = level.parent
    return row


def images_within(class_name: str, row: Base) -> Iterator[Base]:
    """Every image at or beneath a row, whose stored files outlive the rows."""
    if class_name == "Image":
        yield row
    for slot in layout().slots(class_name):
        if slot.kind is SlotKind.LEVEL:
            for child in getattr(row, slot.name):
                yield from images_within(slot.range, child)


# Class-level rules. LinkML's pydanticgen does not turn a schema ``rule`` into a
# validator, so they are evaluated here, against the row as it is about to be
# stored. Only the constructs the schema uses are understood; a new one raises
# rather than passing silently.


def _check_rules(class_name: str, row: Base) -> None:
    for rule in layout().view.get_class(class_name).rules:
        if _holds(rule.preconditions, row) and not _holds(rule.postconditions, row):
            raise SchemaRuleViolation(f"{class_name}: {' '.join(rule.description.split())}")


def _holds(expression: AnonymousClassExpression | None, row: Base) -> bool:
    if expression is None:
        return True
    return all(
        _slot_holds(condition, getattr(row, name))
        for name, condition in expression.slot_conditions.items()
    ) and (not expression.any_of or any(_holds(option, row) for option in expression.any_of))


def _slot_holds(condition: SlotDefinition, value: object) -> bool:
    present = value is not None
    if condition.value_presence is not None:
        return present == (condition.value_presence == PresenceEnum("PRESENT"))
    if condition.equals_string is not None:
        return value == condition.equals_string
    if condition.required:
        return present
    raise NotImplementedError(f"Rule condition on {condition.name} is not understood")
