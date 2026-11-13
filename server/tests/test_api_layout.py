"""The API layout and the LinkML schema must describe the same model."""

from zapp_atlas.api.layout import LEVELS, STANDALONE, SlotKind, layout


def test_every_concrete_class_is_placed() -> None:
    """A class added to the schema fails here until the layout says where it goes."""
    lay = layout()
    concrete = {name for name, cls in lay.view.all_classes().items() if not cls.abstract}
    reached = set().union(*(lay.within(level) for level in LEVELS))

    assert set(LEVELS) <= concrete
    assert set(STANDALONE) <= concrete
    assert concrete - set(LEVELS) - set(STANDALONE) - reached == set()


def test_standalone_classes_are_not_part_of_any_level() -> None:
    lay = layout()
    for level in LEVELS:
        assert not lay.within(level) & set(STANDALONE)
        assert not lay.within(level) & set(LEVELS)


def test_levels_nest_in_the_declared_order() -> None:
    levels = layout().levels
    chain = [(level.name, level.parent and level.parent.name) for level in levels.values()]
    assert chain == [
        ("Study", None),
        ("Experiment", "Study"),
        ("ExposureEvent", "Experiment"),
        ("PhenotypeObservationSet", "ExposureEvent"),
        ("Image", "PhenotypeObservationSet"),
    ]


def test_slots_are_sorted_into_kinds() -> None:
    kinds = {slot.name: slot.kind for slot in layout().slots("ExposureEvent")}
    assert kinds["comment"] is SlotKind.VALUE
    assert kinds["stressor"] is SlotKind.OWNED
    assert kinds["regimen"] is SlotKind.OWNED
    assert kinds["route"] is SlotKind.REFERENCE
    assert kinds["phenotype_observation"] is SlotKind.LEVEL

    study = {slot.name: slot.kind for slot in layout().slots("Study")}
    assert study["research_group"] is SlotKind.VALUE
    assert study["annotator"] is SlotKind.VALUE
