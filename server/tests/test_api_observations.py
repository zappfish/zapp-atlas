from __future__ import annotations

"""API tests for PhenotypeObservationSet endpoints."""

from fastapi.testclient import TestClient


def _create_exposure(client: TestClient) -> int:
    study = client.post(
        "/studies",
        json={
            "publication": "PMID:222",
            "lab": "ZFIN:ZDB-LAB-1-1",
            "annotator": ["ORCID:0000-0000-0000-0000"],
            "experiment": [],
        },
    ).json()
    exp = client.post(
        f"/studies/{study['id']}/experiments",
        json={
            "standard_rearing_condition": True,
            "fish": {"zfin_id": "ZFIN:ZDB-GENO-990101-2", "name": "AB"},
            "control": [],
            "exposure_event": [],
        },
    ).json()
    exposure = client.post(
        f"/experiments/{exp['id']}/exposures",
        json={"stressor": [], "phenotype_observation": []},
    ).json()
    return exposure["id"]


def test_create_observation_for_exposure(client: TestClient) -> None:
    exposure_id = _create_exposure(client)

    payload = {
        "phenotype": [
            {
                "stage": "ZFS:0000035",
                "severity": "moderate",
                "phenotype_term_id": {
                    "term_uri": "ZP:0105827",
                    "term_label": "pericardial region edematous, abnormal",
                },
            }
        ],
        "image": [],
        "control_image": [],
    }

    res = client.post(f"/exposures/{exposure_id}/observations", json=payload)
    assert res.status_code == 201, res.text
    created = res.json()
    assert "id" in created
    assert created["phenotype"][0]["severity"] == "moderate"


def test_create_observation_missing_exposure_404(client: TestClient) -> None:
    res = client.post(
        "/exposures/999999/observations",
        json={"phenotype": [], "image": [], "control_image": []},
    )
    assert res.status_code == 404


def test_get_observation(client: TestClient) -> None:
    exposure_id = _create_exposure(client)
    created = client.post(
        f"/exposures/{exposure_id}/observations",
        json={"phenotype": [], "image": [], "control_image": []},
    ).json()

    res = client.get(f"/observations/{created['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == created["id"]


def test_get_observation_missing_404(client: TestClient) -> None:
    assert client.get("/observations/999999").status_code == 404


def test_patch_observation_replaces_phenotype(client: TestClient) -> None:
    exposure_id = _create_exposure(client)
    created = client.post(
        f"/exposures/{exposure_id}/observations",
        json={
            "phenotype": [
                {
                    "stage": "ZFS:0000035",
                    "severity": "mild",
                    "phenotype_term_id": {
                        "term_uri": "ZP:1",
                        "term_label": "x",
                    },
                }
            ],
            "image": [],
            "control_image": [],
        },
    ).json()

    res = client.patch(
        f"/observations/{created['id']}",
        json={
            "phenotype": [
                {
                    "id": 0,
                    "stage": "ZFS:0000036",
                    "severity": "severe",
                    "phenotype_term_id": {
                        "term_uri": "ZP:2",
                        "term_label": "y",
                    },
                }
            ],
        },
    )
    assert res.status_code == 200, res.text
    patched = res.json()
    assert len(patched["phenotype"]) == 1
    assert patched["phenotype"][0]["severity"] == "severe"


def test_patch_observation_missing_404(client: TestClient) -> None:
    res = client.patch(
        "/observations/999999",
        json={"phenotype": [], "image": [], "control_image": []},
    )
    assert res.status_code == 404
