import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from db import get_db, get_session_factory, init_db
from main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    init_db(engine)
    Session = get_session_factory(engine)

    def _override_get_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Study CRUD lifecycle
# ---------------------------------------------------------------------------

def test_create_study(client):
    r = client.post("/api/studies", json={"publication": "PMID:123"})
    assert r.status_code == 200
    data = r.json()
    assert data["publication"] == "PMID:123"
    assert "id" in data


def test_list_studies(client):
    client.post("/api/studies", json={"publication": "PMID:1"})
    client.post("/api/studies", json={"publication": "PMID:2"})
    r = client.get("/api/studies")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_get_study(client):
    create = client.post("/api/studies", json={"publication": "PMID:42"})
    study_id = create.json()["id"]
    r = client.get(f"/api/studies/{study_id}")
    assert r.status_code == 200
    assert r.json()["publication"] == "PMID:42"


def test_update_study(client):
    create = client.post("/api/studies", json={"publication": "PMID:1"})
    study_id = create.json()["id"]
    r = client.patch(f"/api/studies/{study_id}", json={"publication": "PMID:99"})
    assert r.status_code == 200
    assert r.json()["publication"] == "PMID:99"


def test_delete_study(client):
    create = client.post("/api/studies", json={"publication": "PMID:1"})
    study_id = create.json()["id"]
    r = client.delete(f"/api/studies/{study_id}")
    assert r.status_code == 200
    assert r.json()["ok"] is True

    r = client.get(f"/api/studies/{study_id}")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# 404 on missing entities
# ---------------------------------------------------------------------------

def test_get_missing_study_returns_404(client):
    r = client.get("/api/studies/99999")
    assert r.status_code == 404


def test_update_missing_study_returns_404(client):
    r = client.patch("/api/studies/99999", json={"publication": "x"})
    assert r.status_code == 404


def test_delete_missing_study_returns_404(client):
    r = client.delete("/api/studies/99999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Nested creation — Study with embedded experiments
# ---------------------------------------------------------------------------

def test_create_study_with_experiments(client):
    payload = {
        "publication": "PMID:22194820",
        "experiment": [
            {
                "standard_rearing_condition": True,
                "fish": {
                    "zfin_id": "ZFIN:ZDB-GENO-960809-7",
                    "name": "AB",
                },
                "exposure_event": [
                    {
                        "exposure_start_stage": "ZFS:0000011",
                        "exposure_end_stage": "ZFS:0000039",
                        "stressor": [
                            {
                                "chemical_id": {
                                    "uri": "http://purl.obolibrary.org/obo/CHEBI_33216",
                                    "chebi_id": "CHEBI:33216",
                                    "cas_id": "80-05-7",
                                    "chemical_name": "bisphenol A",
                                },
                                "concentration": {
                                    "unit": "ug/L",
                                    "numeric_value": "100",
                                },
                            }
                        ],
                        "phenotype_observation": [
                            {
                                "phenotype": [
                                    {
                                        "stage": "ZFS:0000035",
                                        "severity": "moderate",
                                        "phenotype_term_id": {
                                            "term_uri": "ZP:0105827",
                                            "term_label": "pericardial region edematous, abnormal",
                                        },
                                    }
                                ]
                            }
                        ],
                    }
                ],
            }
        ],
    }
    r = client.post("/api/studies", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["publication"] == "PMID:22194820"
    assert len(data["experiment"]) == 1

    exp = data["experiment"][0]
    assert exp["standard_rearing_condition"] is True
    assert exp["fish"]["name"] == "AB"

    ee = exp["exposure_event"][0]
    assert ee["exposure_start_stage"] == "ZFS:0000011"
    assert len(ee["stressor"]) == 1
    assert ee["stressor"][0]["chemical_id"]["chemical_name"] == "bisphenol A"
    assert ee["stressor"][0]["concentration"]["numeric_value"] == "100"

    obs = ee["phenotype_observation"][0]
    assert len(obs["phenotype"]) == 1
    assert obs["phenotype"][0]["severity"] == "moderate"
    assert obs["phenotype"][0]["phenotype_term_id"]["term_uri"] == "ZP:0105827"


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------

def test_create_study_rejects_extra_fields(client):
    r = client.post("/api/studies", json={"publication": "PMID:1", "bogus": "field"})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Image CRUD (simple entity)
# ---------------------------------------------------------------------------

def test_image_crud(client):
    r = client.post("/api/images", json={"magnification": "10x"})
    assert r.status_code == 200
    image_id = r.json()["id"]

    r = client.get(f"/api/images/{image_id}")
    assert r.json()["magnification"] == "10x"

    r = client.patch(f"/api/images/{image_id}", json={"magnification": "20x"})
    assert r.json()["magnification"] == "20x"

    r = client.delete(f"/api/images/{image_id}")
    assert r.json()["ok"] is True
