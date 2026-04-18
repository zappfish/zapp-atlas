from __future__ import annotations

"""API tests for Experiment endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from server.api.deps import get_session
from server.api.main import create_app


def _make_test_app():
    from zebrafish_toxicology_atlas_schema.datamodel.sqla import Base  # type: ignore

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    app = create_app()

    def _override_get_session():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = _override_get_session
    return app


def _create_study(client: TestClient) -> int:
    payload = {
        "publication": "PMID:123456",
        "lab": "ZFIN:ZDB-LAB-1-1",
        "annotator": ["ORCID:0000-0000-0000-0000"],
        "experiment": [],
    }
    res = client.post("/studies", json=payload)
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_experiment_create_for_study_then_get_and_list():
    app = _make_test_app()
    client = TestClient(app)

    study_id = _create_study(client)

    exp_payload = {
        "standard_rearing_condition": True,
        "rearing_condition_comment": "",
        "fish": {
            "zfin_id": "ZFIN:ZDB-GENO-960809-7",
            "name": "AB",
        },
        "control": [],
        "exposure_event": [],
    }

    create_res = client.post(f"/studies/{study_id}/experiments", json=exp_payload)
    assert create_res.status_code == 201, create_res.text
    created = create_res.json()
    assert "id" in created

    get_res = client.get(f"/experiments/{created['id']}")
    assert get_res.status_code == 200, get_res.text
    got = get_res.json()
    assert got["id"] == created["id"]

    list_res = client.get("/experiments")
    assert list_res.status_code == 200, list_res.text
    rows = list_res.json()
    assert any(r["id"] == created["id"] for r in rows)


def test_experiment_create_missing_study_404():
    app = _make_test_app()
    client = TestClient(app)

    exp_payload = {
        "standard_rearing_condition": True,
        "fish": {
            "zfin_id": "ZFIN:ZDB-GENO-960809-7",
            "name": "AB",
        },
        "control": [],
        "exposure_event": [],
    }
    res = client.post("/studies/999999/experiments", json=exp_payload)
    assert res.status_code == 404


def test_experiment_get_missing_404():
    app = _make_test_app()
    client = TestClient(app)

    res = client.get("/experiments/999999")
    assert res.status_code == 404


def test_experiment_patch_updates_rearing_and_fish():
    app = _make_test_app()
    client = TestClient(app)

    study_id = _create_study(client)
    exp = client.post(
        f"/studies/{study_id}/experiments",
        json={
            "standard_rearing_condition": True,
            "rearing_condition_comment": "",
            "fish": {"zfin_id": "ZFIN:ZDB-GENO-960809-7", "name": "AB"},
            "control": [],
            "exposure_event": [],
        },
    ).json()

    res = client.patch(
        f"/experiments/{exp['id']}",
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


def test_experiment_patch_missing_404():
    app = _make_test_app()
    client = TestClient(app)

    res = client.patch("/experiments/999999", json={"rearing_condition_comment": "x"})
    assert res.status_code == 404
