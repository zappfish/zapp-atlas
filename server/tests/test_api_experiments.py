"""API tests for Experiment endpoints."""

from fastapi.testclient import TestClient
from support import study_fields


def _create_study(client: TestClient, group: int) -> int:
    payload = {
        "publication": "PMID:123456",
        "lab": "ZFIN:ZDB-LAB-1-1",
        "annotator": ["ORCID:0000-0000-0000-0000"],
        **study_fields(group),
    }
    res = client.post("/api/studies", json=payload)
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_experiment_create_for_study_then_get(client: TestClient, group: int) -> None:
    study_id = _create_study(client, group)

    exp_payload = {
        "standard_rearing_condition": True,
        "rearing_condition_comment": "",
        "fish": {
            "zfin_id": "ZFIN:ZDB-GENO-960809-7",
            "name": "AB",
        },
        "control": [],
    }

    create_res = client.post(f"/api/studies/{study_id}/experiments", json=exp_payload)
    assert create_res.status_code == 201, create_res.text
    created = create_res.json()
    assert "id" in created

    get_res = client.get(f"/api/experiments/{created['id']}")
    assert get_res.status_code == 200, get_res.text
    got = get_res.json()
    assert got["id"] == created["id"]


def test_experiment_create_missing_study_404(client: TestClient, group: int) -> None:
    exp_payload = {
        "standard_rearing_condition": True,
        "fish": {
            "zfin_id": "ZFIN:ZDB-GENO-960809-7",
            "name": "AB",
        },
        "control": [],
    }
    res = client.post("/api/studies/999999/experiments", json=exp_payload)
    assert res.status_code == 404


def test_experiment_get_missing_404(client: TestClient, group: int) -> None:
    res = client.get("/api/experiments/999999")
    assert res.status_code == 404


def test_experiment_put_updates_rearing_and_fish(client: TestClient, group: int) -> None:
    study_id = _create_study(client, group)
    exp = client.post(
        f"/api/studies/{study_id}/experiments",
        json={
            "standard_rearing_condition": True,
            "rearing_condition_comment": "",
            "fish": {"zfin_id": "ZFIN:ZDB-GENO-960809-7", "name": "AB"},
            "control": [],
        },
    ).json()

    res = client.put(
        f"/api/experiments/{exp['id']}",
        json={
            "standard_rearing_condition": False,
            "rearing_condition_comment": "temperature 24C",
            "fish": {"zfin_id": "ZFIN:ZDB-GENO-010112-1", "name": "TU"},
        },
    )
    assert res.status_code == 200, res.text
    patched = res.json()
    assert patched["standard_rearing_condition"] is False
    assert patched["rearing_condition_comment"] == "temperature 24C"
    assert patched["fish"]["zfin_id"] == "ZFIN:ZDB-GENO-010112-1"
    assert patched["fish"]["name"] == "TU"


def test_experiment_put_missing_404(client: TestClient, group: int) -> None:
    res = client.put("/api/experiments/999999", json={"rearing_condition_comment": "x"})
    assert res.status_code == 404
