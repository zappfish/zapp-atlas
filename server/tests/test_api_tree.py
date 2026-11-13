"""Saving a level stores everything its body says, and nothing is left behind."""

import pytest
from sampling import sample
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from zapp_atlas.api.errors import SchemaRuleViolation
from zapp_atlas.api.layout import LEVELS, layout
from zapp_atlas.api.tree import assign, build
from zapp_atlas.schema import pydantic_crud as models
from zapp_atlas.schema import sqla

# The one thing a body of required slots alone cannot satisfy: the rule that an
# unpublished study carries a nickname.
SPARSE = {level: sample(level, full=False) for level in LEVELS}
SPARSE["Study"]["nickname"] = "a working name"


def _comparable(value: object) -> object:
    """Drop generated ids, and treat an empty list and an absent one alike."""
    if isinstance(value, dict):
        return {key: _comparable(item) for key, item in value.items() if key != "id"}
    if isinstance(value, list):
        return [_comparable(item) for item in value] or None
    return value


def _stored(level: str, row: sqla.Base) -> dict[str, object]:
    """What a row reads back as, cut down to the slots a body carries."""
    read = getattr(models, f"{level}Read").model_validate(row).model_dump()
    return {slot.name: _comparable(read[slot.name]) for slot in layout().body_slots(level)}


def _saved(session: Session, level: str, *, full: bool) -> tuple[sqla.Base, dict[str, object]]:
    body = getattr(models, f"{level}Input").model_validate(sample(level, full=full))
    row = build(session, level, body)
    session.add(row)
    session.commit()
    return row, _comparable(body.model_dump())


@pytest.mark.parametrize("level", LEVELS)
def test_every_slot_of_a_level_is_stored(session: Session, level: str) -> None:
    row, body = _saved(session, level, full=True)
    assert _stored(level, row) == body


@pytest.mark.parametrize("level", LEVELS)
def test_replacing_a_level_leaves_nothing_behind(session: Session, level: str) -> None:
    row, _ = _saved(session, level, full=True)
    sparse = getattr(models, f"{level}Input").model_validate(SPARSE[level])

    assign(session, level, row, sparse)
    session.commit()

    assert _stored(level, row) == _comparable(sparse.model_dump())
    lay = layout()
    for class_name in lay.within(level):
        if not lay.is_shared(class_name):
            count = session.scalar(select(func.count()).select_from(getattr(sqla, class_name)))
            assert count == 0, f"{class_name} rows outlived the {level} that owned them"


def test_saving_the_same_body_twice_changes_nothing(session: Session) -> None:
    row, body = _saved(session, "ExposureEvent", full=True)
    assign(session, "ExposureEvent", row, models.ExposureEventInput.model_validate(body))
    session.commit()
    assert _stored("ExposureEvent", row) == body
    assert session.scalar(select(func.count()).select_from(sqla.StressorChemical)) == 1


def test_a_shared_row_used_twice_in_one_body_is_stored_once(session: Session) -> None:
    phenotype = sample("Phenotype", full=True)
    body = models.PhenotypeObservationSetInput.model_validate({"phenotype": [phenotype, phenotype]})
    session.add(build(session, "PhenotypeObservationSet", body))
    session.commit()
    assert session.scalar(select(func.count()).select_from(sqla.PhenotypeTerm)) == 1
    assert session.scalar(select(func.count()).select_from(sqla.Phenotype)) == 2


def test_deleting_a_level_takes_what_it_owns(session: Session) -> None:
    row, _ = _saved(session, "ExposureEvent", full=True)
    session.delete(row)
    session.commit()
    for class_name in ("StressorChemical", "VehicleOfTransmission", "Regimen", "QuantityValue"):
        assert session.scalar(select(func.count()).select_from(getattr(sqla, class_name))) == 0


def test_blank_text_is_stored_as_none(session: Session) -> None:
    body = models.ExperimentInput(rearing_condition_comment="   ")
    assert build(session, "Experiment", body).rearing_condition_comment is None


@pytest.mark.parametrize(
    ("class_name", "body"),
    [
        ("StressorChemical", {}),
        ("StressorChemical", {"chemical_id": "CHEBI:1", "manufacturer": "other_not_listed"}),
        ("VehicleOfTransmission", {"vehicle_type": "other_not_listed"}),
        ("Study", {"research_group": 1}),
        ("Study", {"research_group": 1, "nickname": "  "}),
    ],
)
def test_schema_rules_are_enforced(session: Session, class_name: str, body: dict) -> None:
    with pytest.raises(SchemaRuleViolation):
        build(session, class_name, getattr(models, f"{class_name}Input").model_validate(body))


def test_a_rule_that_is_satisfied_passes(session: Session) -> None:
    body = models.StressorChemicalInput(
        manufacturer="other_not_listed",
        unrecognized_manufacturer_name="A supplier",
        unrecognized_chemical_name="mystery compound",
    )
    assert build(session, "StressorChemical", body).unrecognized_chemical_name
