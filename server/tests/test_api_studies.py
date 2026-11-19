"""API tests for the FastAPI Study endpoints.

These tests are intended to validate the FastAPI wiring + basic CRUD semantics.
"""

from fastapi.testclient import TestClient
from support import make_group, study_fields


def test_study_create_then_get_round_trip_minimal(client: TestClient, group: int) -> None:
    payload = {
        "publication": "PMID:123456",
        "lab": "ZFIN:ZDB-LAB-1-1",
        "annotator": ["ORCID:0000-0000-0000-0000"],
        **study_fields(group),
    }
    create_res = client.post("/api/studies", json=payload)
    assert create_res.status_code == 201, create_res.text
    created = create_res.json()
    assert "id" in created

    get_res = client.get(f"/api/studies/{created['id']}")
    assert get_res.status_code == 200, get_res.text
    got = get_res.json()
    assert got["id"] == created["id"]


def test_study_get_missing_404(client: TestClient, group: int) -> None:
    res = client.get("/api/studies/999999")
    assert res.status_code == 404


def test_study_put_updates_top_level_fields(client: TestClient, group: int) -> None:
    create_payload = {
        "publication": "PMID:123456",
        "lab": "ZFIN:ZDB-LAB-1-1",
        "annotator": ["ORCID:0000-0000-0000-0000"],
        **study_fields(group),
    }
    created = client.post("/api/studies", json=create_payload).json()

    patch_payload = {
        **create_payload,
        "publication": "PMID:654321",
    }
    patch_res = client.put(f"/api/studies/{created['id']}", json=patch_payload)
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
}


def test_unpublished_study_needs_only_a_nickname(client: TestClient, group: int) -> None:
    bare = client.post("/api/studies", json={"nickname": "just a name", **study_fields(group)})
    assert bare.status_code == 201, bare.text
    assert bare.json()["publication"] is None
    assert bare.json()["description"] is None

    res = client.post("/api/studies", json={**UNPUBLISHED, **study_fields(group)})
    assert res.status_code == 201, res.text
    created = res.json()
    assert created["publication"] is None
    assert created["nickname"] == UNPUBLISHED["nickname"]
    assert created["description"] == UNPUBLISHED["description"]

    got = client.get(f"/api/studies/{created['id']}").json()
    assert got["nickname"] == UNPUBLISHED["nickname"]
    assert got["description"] == UNPUBLISHED["description"]


def test_unpublished_study_without_a_nickname_is_rejected(client: TestClient, group: int) -> None:
    """The schema rule: no publication means a nickname is required."""
    res = client.post(
        "/api/studies", json={"description": "no handle at all", **study_fields(group)}
    )
    assert res.status_code == 422, res.text
    assert "nickname" in res.text

    # A blank nickname is not a way around the rule ...
    for blank in ("", "   "):
        res = client.post("/api/studies", json={"nickname": blank, **study_fields(group)})
        assert res.status_code == 422, res.text
    # ... and neither is a blank publication.
    for blank in ("", "   "):
        res = client.post("/api/studies", json={"publication": blank, **study_fields(group)})
        assert res.status_code == 422, res.text


def test_a_blank_publication_is_stored_as_none(client: TestClient, group: int) -> None:
    res = client.post(
        "/api/studies", json={**UNPUBLISHED, **study_fields(group), "publication": "   "}
    )
    assert res.status_code == 201, res.text
    assert res.json()["publication"] is None


def test_a_study_nickname_has_the_same_length_limit_as_the_others(
    client: TestClient, group: int
) -> None:
    res = client.post("/api/studies", json={"nickname": "x" * 200, **study_fields(group)})
    assert res.status_code == 201, res.text
    res = client.post("/api/studies", json={"nickname": "x" * 201, **study_fields(group)})
    assert res.status_code == 422, res.text


def test_a_published_study_may_also_carry_a_nickname(client: TestClient, group: int) -> None:
    res = client.post(
        "/api/studies",
        json={
            "publication": "PMID:123456",
            "nickname": "the 2012 BPA paper",
            **study_fields(group),
        },
    )
    assert res.status_code == 201, res.text
    assert res.json()["nickname"] == "the 2012 BPA paper"
    # ... and the rule does not bite once a publication is present.
    assert res.json()["description"] is None


def test_a_study_nickname_is_unique_within_its_research_group(
    client: TestClient, group: int
) -> None:
    lab_a = make_group(client, "Lab A")
    lab_b = make_group(client, "Lab B")

    first = client.post("/api/studies", json={**UNPUBLISHED, **study_fields(lab_a)})
    assert first.status_code == 201, first.text
    assert first.json()["research_group"] == lab_a

    # The same group cannot use the nickname twice ...
    again = client.post("/api/studies", json={**UNPUBLISHED, **study_fields(lab_a)})
    assert again.status_code == 409, again.text
    # ... but another group may call its own study the same thing.
    other = client.post("/api/studies", json={**UNPUBLISHED, **study_fields(lab_b)})
    assert other.status_code == 201, other.text


def test_a_study_cannot_join_a_research_group_that_does_not_exist(
    client: TestClient, group: int
) -> None:
    # Nobody is a member of a group that does not exist.
    res = client.post("/api/studies", json={**UNPUBLISHED, **study_fields(99999)})
    assert res.status_code == 403, res.text


def test_put_cannot_move_a_study_into_a_group_that_uses_its_nickname(
    client: TestClient, group: int
) -> None:
    lab_a = make_group(client, "Lab A")

    client.post("/api/studies", json={**UNPUBLISHED, **study_fields(lab_a)})
    loose = client.post("/api/studies", json={**UNPUBLISHED, **study_fields(group)}).json()

    res = client.put(f"/api/studies/{loose['id']}", json={**UNPUBLISHED, **study_fields(lab_a)})
    assert res.status_code == 409, res.text
    assert client.get(f"/api/studies/{loose['id']}").json()["research_group"] == group


def test_two_studies_in_a_group_cannot_share_a_nickname(client: TestClient, group: int) -> None:
    assert (
        client.post("/api/studies", json={**UNPUBLISHED, **study_fields(group)}).status_code == 201
    )
    res = client.post("/api/studies", json={**UNPUBLISHED, **study_fields(group)})
    assert res.status_code == 409, res.text

    # Surrounding whitespace does not make a nickname a different one ...
    padded = {
        **UNPUBLISHED,
        **study_fields(group),
        "nickname": f"  {UNPUBLISHED['nickname']}  ",
    }
    assert client.post("/api/studies", json=padded).status_code == 409
    # ... and a published study is held to the same rule.
    published = {
        "publication": "PMID:123456",
        "nickname": UNPUBLISHED["nickname"],
        **study_fields(group),
    }
    assert client.post("/api/studies", json=published).status_code == 409

    # Studies with no nickname at all never collide with each other.
    for pmid in ("PMID:1", "PMID:2"):
        res = client.post("/api/studies", json={"publication": pmid, **study_fields(group)})
        assert res.status_code == 201, res.text


def test_put_cannot_take_another_studys_nickname(client: TestClient, group: int) -> None:
    client.post("/api/studies", json={**UNPUBLISHED, **study_fields(group)})
    other = client.post(
        "/api/studies", json={"nickname": "second pilot", **study_fields(group)}
    ).json()

    res = client.put(
        f"/api/studies/{other['id']}",
        json={"nickname": UNPUBLISHED["nickname"], **study_fields(group)},
    )
    assert res.status_code == 409, res.text
    assert client.get(f"/api/studies/{other['id']}").json()["nickname"] == "second pilot"

    # Sending a study its own nickname back is not a clash.
    res = client.put(
        f"/api/studies/{other['id']}", json={"nickname": "second pilot", **study_fields(group)}
    )
    assert res.status_code == 200, res.text


def test_study_put_renames_a_study(client: TestClient, group: int) -> None:
    created = client.post("/api/studies", json={**UNPUBLISHED, **study_fields(group)}).json()
    res = client.put(
        f"/api/studies/{created['id']}",
        json={
            "nickname": "BPA pilot, round 2",
            "description": "Repeat with a wider series.",
            **study_fields(group),
        },
    )
    assert res.status_code == 200, res.text
    assert res.json()["nickname"] == "BPA pilot, round 2"
    assert res.json()["description"] == "Repeat with a wider series."


def test_reconciling_an_unpublished_study_to_a_pmid_is_a_put(
    client: TestClient, group: int
) -> None:
    """The transition #157 describes: the temp handle gives way to a PMID."""
    created = client.post("/api/studies", json={**UNPUBLISHED, **study_fields(group)}).json()
    res = client.put(
        f"/api/studies/{created['id']}",
        json={**UNPUBLISHED, **study_fields(group), "publication": "PMID:99999"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["publication"] == "PMID:99999"
    # The nickname is sent along and kept: it is still how the lab refers to it.
    assert res.json()["nickname"] == UNPUBLISHED["nickname"]


def test_put_cannot_blank_out_the_publication_of_an_unnamed_study(
    client: TestClient, group: int
) -> None:
    """A study with neither a publication nor a nickname is refused, so none is stranded."""
    created = client.post(
        "/api/studies", json={"publication": "PMID:123456", **study_fields(group)}
    ).json()
    for blank in ("", "   "):
        res = client.put(
            f"/api/studies/{created['id']}", json={"publication": blank, **study_fields(group)}
        )
        assert res.status_code == 422, res.text
        assert client.get(f"/api/studies/{created['id']}").json()["publication"] == "PMID:123456"
