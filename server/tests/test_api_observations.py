"""API tests for PhenotypeObservationSet endpoints."""

from fastapi.testclient import TestClient
from support import study_fields


def _create_exposure(client: TestClient, group: int) -> int:
    study = client.post(
        "/api/studies",
        json={
            "publication": "PMID:222",
            "lab": "ZFIN:ZDB-LAB-1-1",
            "annotator": ["ORCID:0000-0000-0000-0000"],
            **study_fields(group),
        },
    ).json()
    exp = client.post(
        f"/api/studies/{study['id']}/experiments",
        json={
            "standard_rearing_condition": True,
            "fish": {"zfin_id": "ZFIN:ZDB-GENO-990101-2", "name": "AB"},
            "control": [],
        },
    ).json()
    exposure = client.post(
        f"/api/experiments/{exp['id']}/exposures",
        json={"stressor": []},
    ).json()
    return exposure["id"]


def test_create_observation_for_exposure(client: TestClient, group: int) -> None:
    exposure_id = _create_exposure(client, group)

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
        "control_image": [],
    }

    res = client.post(f"/api/exposures/{exposure_id}/observations", json=payload)
    assert res.status_code == 201, res.text
    created = res.json()
    assert "id" in created
    assert created["phenotype"][0]["severity"] == "moderate"


def test_create_observation_missing_exposure_404(client: TestClient, group: int) -> None:
    res = client.post(
        "/api/exposures/999999/observations",
        json={"phenotype": [], "control_image": []},
    )
    assert res.status_code == 404


def test_get_observation(client: TestClient, group: int) -> None:
    exposure_id = _create_exposure(client, group)
    created = client.post(
        f"/api/exposures/{exposure_id}/observations",
        json={"phenotype": [], "control_image": []},
    ).json()

    res = client.get(f"/api/observations/{created['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == created["id"]


def test_get_observation_missing_404(client: TestClient, group: int) -> None:
    assert client.get("/api/observations/999999").status_code == 404


def test_put_observation_replaces_phenotype(client: TestClient, group: int) -> None:
    exposure_id = _create_exposure(client, group)
    created = client.post(
        f"/api/exposures/{exposure_id}/observations",
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
            "control_image": [],
        },
    ).json()

    res = client.put(
        f"/api/observations/{created['id']}",
        json={
            "phenotype": [
                {
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


def test_put_observation_missing_404(client: TestClient, group: int) -> None:
    res = client.put(
        "/api/observations/999999",
        json={"phenotype": [], "control_image": []},
    )
    assert res.status_code == 404
