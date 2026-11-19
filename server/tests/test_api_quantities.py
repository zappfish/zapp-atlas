"""Numbers are held to the types and ranges the schema gives them."""

import pytest
from fastapi.testclient import TestClient
from support import item_url


@pytest.mark.parametrize(
    ("prevalence", "status"),
    [(0, 200), (60.5, 200), (100, 200), (101, 422), (-1, 422), ("most", 422)],
)
def test_prevalence_is_a_percentage(
    client: TestClient, tree: dict, prevalence: object, status: int
) -> None:
    url = item_url("PhenotypeObservationSet", tree["PhenotypeObservationSet"]["id"])
    res = client.put(url, json={"phenotype": [{"prevalence": prevalence}]})
    assert res.status_code == status, res.text


@pytest.mark.parametrize(
    ("concentration", "status"),
    [
        ({"numeric_value": 2.5, "unit": "µM"}, 200),
        ({"numeric_value": 0, "unit": "µM"}, 200),
        ({"numeric_value": -1, "unit": "µM"}, 422),
        ({"numeric_value": "ten", "unit": "µM"}, 422),
        # A unit alone measures nothing.
        ({"unit": "µM"}, 422),
    ],
)
def test_a_quantity_has_a_number_that_is_not_negative(
    client: TestClient, tree: dict, concentration: dict, status: int
) -> None:
    url = item_url("ExposureEvent", tree["ExposureEvent"]["id"])
    stressor = {"chemical_id": "CHEBI:16236", "concentration": concentration}
    res = client.put(url, json={"stressor": [stressor]})
    assert res.status_code == status, res.text


@pytest.mark.parametrize(("count", "status"), [(1, 200), (3, 200), (0, 422), (2.5, 422)])
def test_exposures_are_counted_in_whole_numbers_from_one(
    client: TestClient, tree: dict, count: object, status: int
) -> None:
    url = item_url("ExposureEvent", tree["ExposureEvent"]["id"])
    res = client.put(url, json={"regimen": {"number_of_individual_exposure": count}})
    assert res.status_code == status, res.text
