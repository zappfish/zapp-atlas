from __future__ import annotations

"""API tests for the FastAPI Study endpoints.

These tests are intended to validate the FastAPI wiring + basic CRUD semantics.

Note: per project direction, these may not run yet until:
* the schema package is vendored into this repo and import paths stabilize
* SQLAlchemy models are available on this branch
* dependencies like uvicorn/httpx are installed
"""


from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from zapp_atlas.api.deps import get_session
from zapp_atlas.main import create_app


def _make_test_app():
    """Create an app instance configured with an in-memory sqlite session."""

    # Schema-provided SQLAlchemy base (assumed to exist)
    from zapp_atlas.schema.sqla import Base  # type: ignore

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
    create_res = client.post("/api/studies", json=payload)
    assert create_res.status_code == 201, create_res.text
    created = create_res.json()
    assert "id" in created

    get_res = client.get(f"/api/studies/{created['id']}")
    assert get_res.status_code == 200, get_res.text
    got = get_res.json()
    assert got["id"] == created["id"]


def test_study_get_missing_404():
    app = _make_test_app()
    client = TestClient(app)

    res = client.get("/api/studies/999999")
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
    created = client.post("/api/studies", json=create_payload).json()

    patch_payload = {
        "publication": "PMID:654321",
    }
    patch_res = client.patch(f"/api/studies/{created['id']}", json=patch_payload)
    assert patch_res.status_code == 200, patch_res.text
    patched = patch_res.json()
    assert patched["publication"] == "PMID:654321"


# --------------------------------------------------------------------------- #
# Unpublished studies (#157): no PMID/DOI yet, identified by nickname
# --------------------------------------------------------------------------- #

UNPUBLISHED = {
    "nickname": "BPA dose-response pilot",
    "description": "Pilot exposure of AB embryos to a BPA dilution series, 6-96 hpf.",
    "lab": "ZFIN:ZDB-LAB-1-1",
    "experiment": [],
}


def test_unpublished_study_needs_only_a_nickname():
    app = _make_test_app()
    client = TestClient(app)

    bare = client.post("/api/studies", json={"nickname": "just a name", "experiment": []})
    assert bare.status_code == 201, bare.text
    assert bare.json()["publication"] is None
    assert bare.json()["description"] is None

    res = client.post("/api/studies", json=UNPUBLISHED)
    assert res.status_code == 201, res.text
    created = res.json()
    assert created["publication"] is None
    assert created["nickname"] == UNPUBLISHED["nickname"]
    assert created["description"] == UNPUBLISHED["description"]

    got = client.get(f"/api/studies/{created['id']}").json()
    assert got["nickname"] == UNPUBLISHED["nickname"]
    assert got["description"] == UNPUBLISHED["description"]


def test_unpublished_study_without_a_nickname_is_rejected():
    """The schema rule: no publication means a nickname is required."""
    app = _make_test_app()
    client = TestClient(app)

    res = client.post("/api/studies", json={"description": "no handle at all", "experiment": []})
    assert res.status_code == 422, res.text
    assert "nickname" in res.text

    # A blank nickname is not a way around the rule.
    for blank in ("", "   "):
        res = client.post("/api/studies", json={"nickname": blank, "experiment": []})
        assert res.status_code == 422, res.text


def test_a_published_study_may_also_carry_a_nickname():
    app = _make_test_app()
    client = TestClient(app)

    res = client.post(
        "/api/studies",
        json={"publication": "PMID:123456", "nickname": "the 2012 BPA paper", "experiment": []},
    )
    assert res.status_code == 201, res.text
    assert res.json()["nickname"] == "the 2012 BPA paper"
    # ... and the rule does not bite once a publication is present.
    assert res.json()["description"] is None


def _make_group(app, name: str) -> int:
    """Add a research group straight to the test database."""
    from zapp_atlas.schema.sqla import ResearchGroup  # type: ignore

    sessions = app.dependency_overrides[get_session]()
    session = next(sessions)
    group = ResearchGroup(name=name)
    session.add(group)
    session.commit()
    group_id = group.id
    sessions.close()
    return group_id


def test_a_study_nickname_is_unique_within_its_research_group():
    app = _make_test_app()
    client = TestClient(app)
    lab_a = _make_group(app, "Lab A")
    lab_b = _make_group(app, "Lab B")

    first = client.post("/api/studies", json={**UNPUBLISHED, "research_group": lab_a})
    assert first.status_code == 201, first.text
    assert first.json()["research_group"] == lab_a

    # The same group cannot use the nickname twice ...
    again = client.post("/api/studies", json={**UNPUBLISHED, "research_group": lab_a})
    assert again.status_code == 409, again.text
    # ... but another group may call its own study the same thing.
    other = client.post("/api/studies", json={**UNPUBLISHED, "research_group": lab_b})
    assert other.status_code == 201, other.text
    # So may a study that belongs to no group.
    assert client.post("/api/studies", json=UNPUBLISHED).status_code == 201


def test_a_study_cannot_join_a_research_group_that_does_not_exist():
    app = _make_test_app()
    client = TestClient(app)

    res = client.post("/api/studies", json={**UNPUBLISHED, "research_group": 99999})
    assert res.status_code == 422, res.text


def test_patch_cannot_move_a_study_into_a_group_that_uses_its_nickname():
    app = _make_test_app()
    client = TestClient(app)
    lab_a = _make_group(app, "Lab A")

    client.post("/api/studies", json={**UNPUBLISHED, "research_group": lab_a})
    loose = client.post("/api/studies", json=UNPUBLISHED).json()

    res = client.patch(f"/api/studies/{loose['id']}", json={"research_group": lab_a})
    assert res.status_code == 409, res.text
    assert client.get(f"/api/studies/{loose['id']}").json()["research_group"] is None


def test_two_studies_without_a_group_cannot_share_a_nickname():
    """Studies that belong to no group are held to the rule among themselves."""
    app = _make_test_app()
    client = TestClient(app)

    assert client.post("/api/studies", json=UNPUBLISHED).status_code == 201
    res = client.post("/api/studies", json=UNPUBLISHED)
    assert res.status_code == 409, res.text

    # Surrounding whitespace does not make a nickname a different one ...
    padded = {**UNPUBLISHED, "nickname": f"  {UNPUBLISHED['nickname']}  "}
    assert client.post("/api/studies", json=padded).status_code == 409
    # ... and a published study is held to the same rule.
    published = {"publication": "PMID:123456", "nickname": UNPUBLISHED["nickname"]}
    assert client.post("/api/studies", json=published).status_code == 409

    # Studies with no nickname at all never collide with each other.
    for pmid in ("PMID:1", "PMID:2"):
        res = client.post("/api/studies", json={"publication": pmid, "experiment": []})
        assert res.status_code == 201, res.text


def test_patch_cannot_take_another_studys_nickname():
    app = _make_test_app()
    client = TestClient(app)

    client.post("/api/studies", json=UNPUBLISHED)
    other = client.post("/api/studies", json={"nickname": "second pilot", "experiment": []}).json()

    res = client.patch(f"/api/studies/{other['id']}", json={"nickname": UNPUBLISHED["nickname"]})
    assert res.status_code == 409, res.text
    assert client.get(f"/api/studies/{other['id']}").json()["nickname"] == "second pilot"

    # Sending a study its own nickname back is not a clash.
    res = client.patch(f"/api/studies/{other['id']}", json={"nickname": "second pilot"})
    assert res.status_code == 200, res.text


def test_study_patch_renames_a_study():
    app = _make_test_app()
    client = TestClient(app)

    created = client.post("/api/studies", json=UNPUBLISHED).json()
    res = client.patch(
        f"/api/studies/{created['id']}",
        json={"nickname": "BPA pilot, round 2", "description": "Repeat with a wider series."},
    )
    assert res.status_code == 200, res.text
    assert res.json()["nickname"] == "BPA pilot, round 2"
    assert res.json()["description"] == "Repeat with a wider series."


def test_reconciling_an_unpublished_study_to_a_pmid_is_a_patch():
    """The transition #157 describes: the temp handle gives way to a PMID."""
    app = _make_test_app()
    client = TestClient(app)

    created = client.post("/api/studies", json=UNPUBLISHED).json()
    res = client.patch(f"/api/studies/{created['id']}", json={"publication": "PMID:99999"})
    assert res.status_code == 200, res.text
    assert res.json()["publication"] == "PMID:99999"
    # The nickname survives reconciliation: it is still how the lab refers to it.
    assert res.json()["nickname"] == UNPUBLISHED["nickname"]


def test_patch_cannot_leave_an_unpublished_study_anonymous():
    """The rule is re-checked on PATCH, not just POST."""
    app = _make_test_app()
    client = TestClient(app)

    created = client.post(
        "/api/studies", json={"publication": "PMID:123456", "experiment": []}
    ).json()
    # Blanking the publication on a study with no nickname would strand it.
    res = client.patch(f"/api/studies/{created['id']}", json={"publication": ""})
    assert res.status_code == 422, res.text
    assert client.get(f"/api/studies/{created['id']}").json()["publication"] == "PMID:123456"
