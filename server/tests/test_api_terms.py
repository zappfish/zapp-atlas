"""A term a request names is checked against the reference bundle.

The tests' bundle (``tests/labels_fixture``) holds a few ZP, ZFA and ChEBI
terms and nothing from ECTO, as the real one holds none.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from support import item_url, make_group, signin

EDEMA = {"term_uri": "ZP:0105827", "term_label": "edematous pericardial region"}


def _phenotype(client: TestClient, tree: dict, term: dict):
    url = item_url("PhenotypeObservationSet", tree["PhenotypeObservationSet"]["id"])
    return client.put(url, json={"phenotype": [{"phenotype_term_id": term}]})


def _stressor(client: TestClient, tree: dict, chemical_id: str):
    url = item_url("ExposureEvent", tree["ExposureEvent"]["id"])
    return client.put(url, json={"stressor": [{"chemical_id": chemical_id}]})


def test_a_terms_label_is_the_bundles_whatever_the_body_says(
    client: TestClient, tree: dict
) -> None:
    res = _phenotype(client, tree, {"term_uri": "ZP:0105827", "term_label": "swollen heart"})
    assert res.status_code == 200, res.text
    assert res.json()["phenotype"][0]["phenotype_term_id"] == EDEMA

    # And when the body gives no label at all.
    res = _phenotype(client, tree, {"term_uri": "ZP:0105827"})
    assert res.json()["phenotype"][0]["phenotype_term_id"] == EDEMA


@pytest.mark.parametrize(
    "term_uri",
    [
        "ZP:9999999",  # no such term
        "ZFA:0000114",  # a real term, of an ontology a phenotype is not from
        "pericardial edema",  # not an id at all
    ],
)
def test_a_phenotype_is_a_zp_term_the_bundle_has(
    client: TestClient, tree: dict, term_uri: str
) -> None:
    res = _phenotype(client, tree, {"term_uri": term_uri, "term_label": "anything"})
    assert res.status_code == 422, res.text
    assert term_uri in res.text


@pytest.mark.parametrize(
    ("chemical_id", "status"),
    [("CHEBI:41774", 200), ("CHEBI:999999999", 422), ("CAS:10540-29-1", 422)],
)
def test_a_stressors_chemical_is_a_chebi_term_the_bundle_has(
    client: TestClient, tree: dict, chemical_id: str, status: int
) -> None:
    assert _stressor(client, tree, chemical_id).status_code == status


def test_a_cabinet_holds_chemicals_the_bundle_has(client: TestClient, group: int) -> None:
    url = f"/api/research-groups/{group}/chemical-cabinet"
    assert client.post(url, json={"chemical_id": "CHEBI:41774"}).status_code == 201
    assert client.post(url, json={"chemical_id": "CHEBI:999999999"}).status_code == 422


def test_a_term_the_bundle_has_no_ontology_for_keeps_the_label_it_was_sent(
    client: TestClient, tree: dict
) -> None:
    """The bundle has nothing from ECTO, so an exposure type is held to its prefix."""
    url = item_url("ExposureEvent", tree["ExposureEvent"]["id"])
    sent = {"term_uri": "ECTO:9000057", "term_label": "exposure to bisphenol A"}

    res = client.put(url, json={"exposure_type": sent})
    assert res.status_code == 200, res.text
    assert res.json()["exposure_type"] == sent

    wrong = {"term_uri": "ZP:0105827", "term_label": "a phenotype"}
    assert client.put(url, json={"exposure_type": wrong}).status_code == 422


@pytest.mark.parametrize(
    "stage",
    [
        "ZFS:9999999",  # no such stage
        "ZP:0105827",  # a real term that is not a stage
        "72 hpf",  # a time, which the form turns into a stage
    ],
)
def test_a_stage_is_one_of_zfins(client: TestClient, tree: dict, stage: str) -> None:
    exposure = item_url("ExposureEvent", tree["ExposureEvent"]["id"])
    assert client.put(exposure, json={"exposure_start_stage": stage}).status_code == 422

    observation = item_url("PhenotypeObservationSet", tree["PhenotypeObservationSet"]["id"])
    assert client.put(observation, json={"phenotype": [{"stage": stage}]}).status_code == 422


def test_an_exposure_does_not_end_before_it_started(client: TestClient, tree: dict) -> None:
    url = item_url("ExposureEvent", tree["ExposureEvent"]["id"])
    shield, day_5 = "ZFS:0000019", "ZFS:0000037"

    forward = {"exposure_start_stage": shield, "exposure_end_stage": day_5}
    assert client.put(url, json=forward).status_code == 200
    # Starting and ending within one stage is an exposure shorter than the stage.
    within = {"exposure_start_stage": shield, "exposure_end_stage": shield}
    assert client.put(url, json=within).status_code == 200

    backward = client.put(url, json={"exposure_start_stage": day_5, "exposure_end_stage": shield})
    assert backward.status_code == 422, backward.text
    assert "is before" in backward.text


class TestWithNoBundle:
    @pytest.fixture
    def extdata_dir(self, tmp_path_factory) -> Path:
        return tmp_path_factory.mktemp("no-bundle")

    def test_a_term_is_not_stored_unchecked(self, client: TestClient) -> None:
        signin(client, "0000-0002-1825-0097")
        group = make_group(client, "Test Lab")
        res = client.post(
            f"/api/research-groups/{group}/chemical-cabinet", json={"chemical_id": "CHEBI:41774"}
        )
        assert res.status_code == 503, res.text
        assert "reference data" in res.json()["detail"]
