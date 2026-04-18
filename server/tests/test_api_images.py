from __future__ import annotations

"""API tests for image upload/fetch.

Local-filesystem backend only; S3/Tigris path is env-gated and not
exercised here.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient


# Tiny valid PNG: 1x1 pixel, red. Small enough to embed.
_PNG_1X1_RED = bytes.fromhex(
    "89504E470D0A1A0A0000000D49484452000000010000000108020000"
    "00907753DE0000000C4944415408D76368F8FF1F0000040100017F3F"
    "8F180000000049454E44AE426082"
)


@pytest.fixture(autouse=True)
def _tmp_upload_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the local storage backend at a per-test tmp dir."""
    monkeypatch.setenv("ZAPP_UPLOAD_DIR", str(tmp_path))
    monkeypatch.delenv("AWS_ENDPOINT_URL_S3", raising=False)
    return tmp_path


def _create_observation(client: TestClient) -> int:
    study = client.post(
        "/studies",
        json={
            "publication": "PMID:img-1",
            "lab": "ZFIN:ZDB-LAB-1-1",
            "annotator": ["ORCID:0000-0000-0000-0000"],
            "experiment": [],
        },
    ).json()
    exp = client.post(
        f"/studies/{study['id']}/experiments",
        json={
            "standard_rearing_condition": True,
            "fish": {"zfin_id": "ZFIN:ZDB-GENO-990101-4", "name": "AB"},
            "control": [],
            "exposure_event": [],
        },
    ).json()
    exposure = client.post(
        f"/experiments/{exp['id']}/exposures",
        json={"stressor": [], "phenotype_observation": []},
    ).json()
    obs = client.post(
        f"/exposures/{exposure['id']}/observations",
        json={"phenotype": [], "image": [], "control_image": []},
    ).json()
    return obs["id"]


def test_upload_image_and_fetch_round_trip(client: TestClient) -> None:
    obs_id = _create_observation(client)

    upload = client.post(
        f"/observations/{obs_id}/images",
        files={"file": ("fish.png", _PNG_1X1_RED, "image/png")},
        data={"magnification": "40x", "resolution": "1024x1024", "scale_bar": "100um"},
    )
    assert upload.status_code == 201, upload.text
    created = upload.json()
    assert "id" in created
    assert created["magnification"] == "40x"

    fetch = client.get(f"/images/{created['id']}")
    assert fetch.status_code == 200
    assert fetch.headers["content-type"] == "image/png"
    assert fetch.content == _PNG_1X1_RED


def test_uploaded_image_appears_in_observation_read(client: TestClient) -> None:
    obs_id = _create_observation(client)
    upload = client.post(
        f"/observations/{obs_id}/images",
        files={"file": ("a.png", _PNG_1X1_RED, "image/png")},
    ).json()

    got = client.get(f"/observations/{obs_id}").json()
    assert len(got["image"]) == 1
    assert got["image"][0]["id"] == upload["id"]


def test_upload_rejects_non_image_content_type(client: TestClient) -> None:
    obs_id = _create_observation(client)
    res = client.post(
        f"/observations/{obs_id}/images",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert res.status_code == 415


def test_upload_rejects_oversized(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ZAPP_MAX_UPLOAD_BYTES", "64")

    obs_id = _create_observation(client)
    big = b"\x89PNG\r\n\x1a\n" + (b"\x00" * 1024)
    res = client.post(
        f"/observations/{obs_id}/images",
        files={"file": ("big.png", big, "image/png")},
    )
    assert res.status_code == 413


def test_upload_missing_observation_404(client: TestClient) -> None:
    res = client.post(
        "/observations/999999/images",
        files={"file": ("a.png", _PNG_1X1_RED, "image/png")},
    )
    assert res.status_code == 404


def test_get_missing_image_404(client: TestClient) -> None:
    assert client.get("/images/999999").status_code == 404
