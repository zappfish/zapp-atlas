from __future__ import annotations

"""Cascade delete tests across the study → observation hierarchy."""

from pathlib import Path

from fastapi.testclient import TestClient


_PNG_1X1_RED = bytes.fromhex(
    "89504E470D0A1A0A0000000D49484452000000010000000108020000"
    "00907753DE0000000C4944415408D76368F8FF1F0000040100017F3F"
    "8F180000000049454E44AE426082"
)


def _build_study_graph(client: TestClient) -> dict:
    """Create a full study → experiment → exposure → observation + image
    for delete-cascade testing. Returns the ids."""
    study = client.post(
        "/api/studies",
        json={
            "publication": "PMID:delete-1",
            "lab": "ZFIN:ZDB-LAB-1-1",
            "annotator": ["ORCID:0000-0000-0000-0000"],
            "experiment": [],
        },
    ).json()
    exp = client.post(
        f"/api/studies/{study['id']}/experiments",
        json={
            "standard_rearing_condition": True,
            "fish": {"zfin_id": "ZFIN:ZDB-GENO-960809-7", "name": "AB"},
            "control": [],
            "exposure_event": [],
        },
    ).json()
    exposure = client.post(
        f"/api/experiments/{exp['id']}/exposures",
        json={"stressor": [], "phenotype_observation": []},
    ).json()
    obs = client.post(
        f"/api/exposures/{exposure['id']}/observations",
        json={"phenotype": [], "image": [], "control_image": []},
    ).json()
    image = client.post(
        f"/api/observations/{obs['id']}/images",
        files={"file": ("a.png", _PNG_1X1_RED, "image/png")},
    ).json()
    return {
        "study_id": study["id"],
        "experiment_id": exp["id"],
        "exposure_id": exposure["id"],
        "observation_id": obs["id"],
        "image_id": image["id"],
    }


def test_delete_image_removes_row_and_blob(
    client: TestClient, tmp_path: Path
) -> None:
    ids = _build_study_graph(client)
    blob = tmp_path / "images" / str(ids["image_id"])
    assert blob.is_file()

    res = client.delete(f"/api/images/{ids['image_id']}")
    assert res.status_code == 204

    assert client.get(f"/api/images/{ids['image_id']}").status_code == 404
    assert not blob.exists()


def test_delete_observation_cascades_to_images(
    client: TestClient, tmp_path: Path
) -> None:
    ids = _build_study_graph(client)

    res = client.delete(f"/api/observations/{ids['observation_id']}")
    assert res.status_code == 204

    assert client.get(f"/api/observations/{ids['observation_id']}").status_code == 404
    assert client.get(f"/api/images/{ids['image_id']}").status_code == 404


def test_delete_exposure_cascades(client: TestClient) -> None:
    ids = _build_study_graph(client)

    res = client.delete(f"/api/exposures/{ids['exposure_id']}")
    assert res.status_code == 204

    assert client.get(f"/api/exposures/{ids['exposure_id']}").status_code == 404
    assert client.get(f"/api/observations/{ids['observation_id']}").status_code == 404
    assert client.get(f"/api/images/{ids['image_id']}").status_code == 404


def test_delete_experiment_cascades(client: TestClient) -> None:
    ids = _build_study_graph(client)

    res = client.delete(f"/api/experiments/{ids['experiment_id']}")
    assert res.status_code == 204

    assert client.get(f"/api/experiments/{ids['experiment_id']}").status_code == 404
    assert client.get(f"/api/exposures/{ids['exposure_id']}").status_code == 404
    assert client.get(f"/api/observations/{ids['observation_id']}").status_code == 404


def test_delete_study_cascades_all_the_way_down(client: TestClient) -> None:
    ids = _build_study_graph(client)

    res = client.delete(f"/api/studies/{ids['study_id']}")
    assert res.status_code == 204

    assert client.get(f"/api/studies/{ids['study_id']}").status_code == 404
    assert client.get(f"/api/experiments/{ids['experiment_id']}").status_code == 404
    assert client.get(f"/api/exposures/{ids['exposure_id']}").status_code == 404
    assert client.get(f"/api/observations/{ids['observation_id']}").status_code == 404
    assert client.get(f"/api/images/{ids['image_id']}").status_code == 404


def test_delete_missing_entities_404(client: TestClient) -> None:
    for path in (
        "/api/studies/999999",
        "/api/experiments/999999",
        "/api/exposures/999999",
        "/api/observations/999999",
        "/api/images/999999",
    ):
        assert client.delete(path).status_code == 404
