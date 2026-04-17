from __future__ import annotations

"""API tests for the FastAPI Study endpoints.

These tests are intended to validate the FastAPI wiring + basic CRUD semantics.

Note: per project direction, these may not run yet until:
* the schema package is vendored into this repo and import paths stabilize
* SQLAlchemy models are available on this branch
* dependencies like uvicorn/httpx are installed
"""

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from server.api.deps import get_session
from server.api.main import create_app


def _make_test_app():
    """Create an app instance configured with an in-memory sqlite session."""

    # Schema-provided SQLAlchemy base (assumed to exist)
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


def test_study_create_then_get_round_trip_minimal():
    app = _make_test_app()
    client = TestClient(app)

    payload = {
        "publication": "PMID:123456",
        "lab": "ZFIN:ZDB-LAB-1-1",
        "annotator": ["ORCID:0000-0000-0000-0000"],
        "experiment": [],
    }
    create_res = client.post("/studies", json=payload)
    assert create_res.status_code == 201, create_res.text
    created = create_res.json()
    assert "id" in created

    get_res = client.get(f"/studies/{created['id']}")
    assert get_res.status_code == 200, get_res.text
    got = get_res.json()
    assert got["id"] == created["id"]


def test_study_get_missing_404():
    app = _make_test_app()
    client = TestClient(app)

    res = client.get("/studies/999999")
    assert res.status_code == 404


def test_study_patch_updates_top_level_fields():
    app = _make_test_app()
    client = TestClient(app)

    create_payload = {
        "publication": "PMID:123456",
        "lab": "ZFIN:ZDB-LAB-1-1",
        "annotator": ["ORCID:0000-0000-0000-0000"],
        "experiment": [],
    }
    created = client.post("/studies", json=create_payload).json()

    patch_payload = {
        "publication": "PMID:654321",
    }
    patch_res = client.patch(f"/studies/{created['id']}", json=patch_payload)
    assert patch_res.status_code == 200, patch_res.text
    patched = patch_res.json()
    assert patched["publication"] == "PMID:654321"
