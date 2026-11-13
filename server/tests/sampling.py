"""Request bodies built from the schema itself.

A test that writes its bodies out by hand covers the slots someone remembered.
These cover every slot the schema declares, so a slot added later is exercised
without anyone editing a test.
"""

from zapp_atlas.api.layout import Slot, SlotKind, layout

_SCALARS = {
    "string": "some text",
    "integer": 1,
    "boolean": True,
    "uriorcurie": "EXAMPLE:1",
}


def sample(class_name: str, *, full: bool) -> dict[str, object]:
    """A body for a class: every slot it carries, or only the required ones."""
    lay = layout()
    induced = {slot.name: slot for slot in lay.view.class_induced_slots(class_name)}
    carried = lay.slots(class_name) if lay.is_shared(class_name) else lay.body_slots(class_name)
    return {
        slot.name: [_value(slot)] if slot.multivalued else _value(slot)
        for slot in carried
        if full or induced[slot.name].required
    }


def _value(slot: Slot) -> object:
    view = layout().view
    induced = view.get_slot(slot.name)
    if slot.kind is not SlotKind.VALUE:
        return sample(slot.range, full=True)
    if induced.examples:
        return induced.examples[0].value
    if slot.range in view.all_enums():
        return next(iter(view.get_enum(slot.range).permissible_values))
    if slot.range in view.all_classes():
        return 1  # the id of a row that lives elsewhere
    return _SCALARS[slot.range]
