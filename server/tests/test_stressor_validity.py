"""Schema rules that the generated validators cannot enforce.

LinkML's pydanticgen does not turn class-level ``rules`` into validators, so
the chemical identifiability rule and the ``other_not_listed`` escape-hatch
rules are re-checked by guards in the study service. Lock those guards in, and
check they surface as 422 rather than escaping as a 500.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from zapp_atlas.api.errors import SchemaRuleViolation
from zapp_atlas.api.services.studies import _stressor_from_create, _vehicle_from_payload
from zapp_atlas.schema.pydantic_crud import StressorChemicalCreate, VehicleOfTransmissionCreate


@pytest.fixture
def session() -> Session:
    """The guards run before any query, so an unusable session is enough.

    Passing a real one would suggest the guard depends on it; passing None
    would lie about the parameter's type.
    """
    return Session()


def test_stressor_must_have_chemical_id_or_unrecognized_name(session: Session) -> None:
    with pytest.raises(SchemaRuleViolation):
        _stressor_from_create(session, StressorChemicalCreate())

    # The free-text fallback alone is enough to be valid.
    stressor = _stressor_from_create(
        session, StressorChemicalCreate(unrecognized_chemical_name="weird compound X")
    )
    assert stressor.unrecognized_chemical_name == "weird compound X"


def test_other_not_listed_manufacturer_needs_a_name(session: Session) -> None:
    with pytest.raises(SchemaRuleViolation):
        _stressor_from_create(
            session,
            StressorChemicalCreate(chemical_id="CHEBI:1", manufacturer="other_not_listed"),
        )

    stressor = _stressor_from_create(
        session,
        StressorChemicalCreate(
            chemical_id="CHEBI:1",
            manufacturer="other_not_listed",
            unrecognized_manufacturer_name="Acme Reagents",
        ),
    )
    assert stressor.unrecognized_manufacturer_name == "Acme Reagents"


def test_other_not_listed_vehicle_needs_a_name() -> None:
    with pytest.raises(SchemaRuleViolation):
        _vehicle_from_payload(VehicleOfTransmissionCreate(vehicle_type="other_not_listed"))

    vehicle = _vehicle_from_payload(
        VehicleOfTransmissionCreate(
            vehicle_type="other_not_listed", unrecognized_chemical_name="odd buffer"
        )
    )
    assert vehicle.unrecognized_chemical_name == "odd buffer"


def _experiment(client: TestClient) -> int:
    study = client.post(
        "/api/studies",
        json={
            "publication": "PMID:1",
            "lab": "ZFIN:ZDB-LAB-1-1",
            "annotator": ["ORCID:0000-0000-0000-0000"],
            "experiment": [],
        },
    ).json()
    exp = client.post(
        f"/api/studies/{study['id']}/experiments",
        json={
            "standard_rearing_condition": True,
            "fish": {"zfin_id": "ZFIN:ZDB-GENO-990101-1", "name": "AB"},
            "control": [],
            "exposure_event": [],
        },
    ).json()
    return exp["id"]


@pytest.mark.parametrize(
    ("stressor", "vehicle"),
    [
        pytest.param({"cas_id": "80-05-7"}, None, id="no-identity"),
        pytest.param(
            {"chemical_id": "CHEBI:1", "manufacturer": "other_not_listed"},
            None,
            id="unnamed-manufacturer",
        ),
        pytest.param(
            {"chemical_id": "CHEBI:1"},
            {"vehicle_type": "other_not_listed"},
            id="unnamed-vehicle",
        ),
    ],
)
def test_rule_violations_are_422_not_500(
    client: TestClient, stressor: dict, vehicle: dict | None
) -> None:
    payload: dict = {"stressor": [stressor], "phenotype_observation": []}
    if vehicle is not None:
        payload["vehicle"] = [vehicle]

    res = client.post(f"/api/experiments/{_experiment(client)}/exposures", json=payload)

    assert res.status_code == 422, res.text


def test_a_fully_named_escape_hatch_entry_is_accepted(client: TestClient) -> None:
    res = client.post(
        f"/api/experiments/{_experiment(client)}/exposures",
        json={
            "vehicle": [
                {"vehicle_type": "other_not_listed", "unrecognized_chemical_name": "odd buffer"}
            ],
            "stressor": [
                {
                    "chemical_id": "CHEBI:1",
                    "manufacturer": "other_not_listed",
                    "unrecognized_manufacturer_name": "Acme Reagents",
                }
            ],
            "phenotype_observation": [],
        },
    )

    assert res.status_code == 201, res.text
