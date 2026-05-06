from __future__ import annotations

"""API tests for Exposure event endpoints."""

from fastapi.testclient import TestClient


def _create_study_and_experiment(client: TestClient) -> tuple[int, int]:
    study = client.post(
        "/api/studies",
        json={
            "publication": "PMID:111",
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
    return study["id"], exp["id"]


def test_create_exposure_for_experiment(client: TestClient) -> None:
    _, exp_id = _create_study_and_experiment(client)

    payload = {
        "exposure_start_stage": "ZFS:0000011",
        "exposure_end_stage": "ZFS:0000039",
        "stressor": [
            {
                "chemical_id": "CHEBI:33216",
                "cas_id": "80-05-7",
                "chemical_name": "bisphenol A",
                "concentration": {"unit": "µg/L", "numeric_value": "100"},
            }
        ],
        "phenotype_observation": [],
    }

    res = client.post(f"/api/experiments/{exp_id}/exposures", json=payload)
    assert res.status_code == 201, res.text
    created = res.json()
    assert "id" in created
    assert created["exposure_start_stage"] == "ZFS:0000011"
    assert created["stressor"][0]["chemical_id"] == "CHEBI:33216"


def test_create_exposure_missing_experiment_404(client: TestClient) -> None:
    res = client.post(
        "/api/experiments/999999/exposures",
        json={"stressor": [], "phenotype_observation": []},
    )
    assert res.status_code == 404


def test_get_exposure(client: TestClient) -> None:
    _, exp_id = _create_study_and_experiment(client)
    created = client.post(
        f"/api/experiments/{exp_id}/exposures",
        json={"stressor": [], "phenotype_observation": []},
    ).json()

    res = client.get(f"/api/exposures/{created['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == created["id"]


def test_get_exposure_missing_404(client: TestClient) -> None:
    assert client.get("/api/exposures/999999").status_code == 404


def test_patch_exposure_updates_fields(client: TestClient) -> None:
    _, exp_id = _create_study_and_experiment(client)
    created = client.post(
        f"/api/experiments/{exp_id}/exposures",
        json={
            "comment": "",
            "exposure_start_stage": "ZFS:0000011",
            "stressor": [],
            "phenotype_observation": [],
        },
    ).json()

    res = client.patch(
        f"/api/exposures/{created['id']}",
        json={"comment": "revised note", "exposure_start_stage": "ZFS:0000012"},
    )
    assert res.status_code == 200, res.text
    patched = res.json()
    assert patched["comment"] == "revised note"
    assert patched["exposure_start_stage"] == "ZFS:0000012"


def test_patch_exposure_missing_404(client: TestClient) -> None:
    assert client.patch("/api/exposures/999999", json={"comment": "x"}).status_code == 404


# -- ontology-backed fields round-trip as {term_uri, term_label} objects ------
# No server-side validation in this pass; clients are expected to pick the
# term via autocomplete and send both the URI and the label.


def test_create_exposure_with_route_round_trips(client: TestClient) -> None:
    _, exp_id = _create_study_and_experiment(client)

    res = client.post(
        f"/api/experiments/{exp_id}/exposures",
        json={
            "route": {
                "term_uri": "ExO:0000057",
                "term_label": "inhalation route",
            },
            "exposure_type": {
                "term_uri": "ECTO:9000057",
                "term_label": "exposure to bisphenol A",
            },
            "stressor": [],
            "phenotype_observation": [],
        },
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["route"] == {
        "term_uri": "ExO:0000057",
        "term_label": "inhalation route",
    }
    assert body["exposure_type"] == {
        "term_uri": "ECTO:9000057",
        "term_label": "exposure to bisphenol A",
    }

    got = client.get(f"/api/exposures/{body['id']}").json()
    assert got["route"]["term_label"] == "inhalation route"
    assert got["exposure_type"]["term_label"] == "exposure to bisphenol A"


def test_patch_exposure_replaces_route(client: TestClient) -> None:
    _, exp_id = _create_study_and_experiment(client)

    created = client.post(
        f"/api/experiments/{exp_id}/exposures",
        json={
            "route": {
                "term_uri": "ExO:0000057",
                "term_label": "inhalation route",
            },
            "stressor": [],
            "phenotype_observation": [],
        },
    ).json()

    res = client.patch(
        f"/api/exposures/{created['id']}",
        json={
            "route": {
                "term_uri": "ExO:0000056",
                "term_label": "dermal route",
            }
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["route"]["term_uri"] == "ExO:0000056"
    assert body["route"]["term_label"] == "dermal route"
