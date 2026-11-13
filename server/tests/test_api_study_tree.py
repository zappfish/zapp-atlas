"""The study tree over HTTP: each level is created, read, replaced and deleted as a unit."""

import pytest
from fastapi.testclient import TestClient
from support import (
    CURATOR,
    JSON_LEVELS,
    OUTSIDER,
    SEGMENTS,
    body,
    carried,
    collection_url,
    comparable,
    item_url,
    make_group,
    signin,
    signout,
)

from zapp_atlas.api.layout import SlotKind, layout


def _next_level_slot(level: str) -> str | None:
    return next((s.name for s in layout().slots(level) if s.kind is SlotKind.LEVEL), None)


@pytest.mark.parametrize("level", JSON_LEVELS)
def test_a_level_reads_back_as_it_was_created(
    client: TestClient, group: int, tree: dict, level: str
) -> None:
    read = client.get(item_url(level, tree[level]["id"]))
    assert read.status_code == 200
    assert carried(level, read.json()) == comparable(body(level, group))


def test_reading_a_study_returns_the_whole_tree(client: TestClient, tree: dict) -> None:
    study = client.get(item_url("Study", tree["Study"]["id"])).json()
    [experiment] = study["experiment"]
    [exposure] = experiment["exposure_event"]
    [observation] = exposure["phenotype_observation"]
    assert observation["id"] == tree["PhenotypeObservationSet"]["id"]
    assert observation["phenotype"]


@pytest.mark.parametrize("level", JSON_LEVELS)
def test_put_replaces_a_level_and_leaves_the_next_one_alone(
    client: TestClient, group: int, tree: dict, level: str
) -> None:
    url = item_url(level, tree[level]["id"])
    sparse = body(level, group, full=False)

    res = client.put(url, json=sparse)

    assert res.status_code == 200, res.text
    stored = carried(level, client.get(url).json())
    assert stored == dict.fromkeys(stored) | comparable(sparse)
    below = _next_level_slot(level)
    if below is not None and level != "PhenotypeObservationSet":
        assert len(client.get(url).json()[below]) == 1


def test_put_clears_what_the_body_leaves_out(client: TestClient, tree: dict) -> None:
    url = item_url("Experiment", tree["Experiment"]["id"])
    assert client.get(url).json()["rearing_condition_comment"]
    client.put(url, json={})
    assert client.get(url).json()["rearing_condition_comment"] is None
    assert client.get(url).json()["control"] in (None, [])


@pytest.mark.parametrize("level", JSON_LEVELS)
def test_delete_takes_everything_beneath_a_level(
    client: TestClient, tree: dict, level: str
) -> None:
    assert client.delete(item_url(level, tree[level]["id"])).status_code == 204

    at_or_below = JSON_LEVELS[JSON_LEVELS.index(level) :]
    for other in JSON_LEVELS:
        expected = 404 if other in at_or_below else 200
        assert client.get(item_url(other, tree[other]["id"])).status_code == expected


@pytest.mark.parametrize("level", JSON_LEVELS[:-1])
def test_a_body_may_not_carry_the_next_level(
    client: TestClient, group: int, tree: dict, level: str
) -> None:
    """The next level down is saved through its own routes, never inside its parent."""
    parent = layout().levels[level].parent
    url = collection_url(level, parent and tree[parent.name]["id"])
    res = client.post(url, json={**body(level, group), _next_level_slot(level): []})
    assert res.status_code == 422


def test_a_missing_row_is_a_404(client: TestClient, group: int) -> None:
    for level in JSON_LEVELS:
        assert client.get(item_url(level, 999)).status_code == 404
        assert client.put(item_url(level, 999), json=body(level, group)).status_code == 404


# -- studies ---------------------------------------------------------------


def test_listing_studies_gives_summaries(client: TestClient, tree: dict) -> None:
    [listed] = client.get("/api/studies").json()
    assert listed["id"] == tree["Study"]["id"]
    assert listed["nickname"] == tree["Study"]["nickname"]
    assert "experiment" not in listed


def test_studies_can_be_listed_by_research_group(client: TestClient, tree: dict) -> None:
    other = make_group(client, "Other Lab")
    client.post("/api/studies", json=body("Study", other))

    listed = client.get("/api/studies", params={"research_group": other}).json()
    assert [study["research_group"] for study in listed] == [other]
    assert len(client.get("/api/studies").json()) == 2


def test_a_nickname_is_unique_within_a_research_group(client: TestClient, group: int) -> None:
    named = {"research_group": group, "nickname": "BPA pilot"}
    assert client.post("/api/studies", json=named).status_code == 201

    again = client.post("/api/studies", json=named)
    assert again.status_code == 409
    assert "nickname" in again.json()["detail"]

    other = make_group(client, "Other Lab")
    assert client.post("/api/studies", json={**named, "research_group": other}).status_code == 201


def test_a_nickname_is_at_most_200_characters(client: TestClient, group: int) -> None:
    res = client.post("/api/studies", json={"research_group": group, "nickname": "x" * 201})
    assert res.status_code == 422


def test_a_schema_rule_is_a_422(client: TestClient, group: int, tree: dict) -> None:
    unnamed = client.post("/api/studies", json={"research_group": group})
    assert unnamed.status_code == 422
    assert unnamed.json()["detail"][0]["type"] == "schema_rule"

    unidentified = client.put(
        item_url("ExposureEvent", tree["ExposureEvent"]["id"]),
        json={"stressor": [{"manufacturer": "sigma_aldrich"}]},
    )
    assert unidentified.status_code == 422
    # And the exposure is as it was.
    stored = client.get(item_url("ExposureEvent", tree["ExposureEvent"]["id"])).json()
    assert stored["stressor"][0]["chemical_id"]


# -- who may do what -------------------------------------------------------


def test_anyone_may_read(client: TestClient, tree: dict) -> None:
    signout(client)
    for level in JSON_LEVELS:
        assert client.get(item_url(level, tree[level]["id"])).status_code == 200
    assert client.get("/api/studies").status_code == 200


@pytest.mark.parametrize(("who", "status"), [(None, 401), (OUTSIDER, 403)])
@pytest.mark.parametrize("level", JSON_LEVELS)
def test_only_a_member_of_the_studys_group_may_write(
    client: TestClient, group: int, tree: dict, level: str, who: str | None, status: int
) -> None:
    signout(client)
    if who is not None:
        signin(client, who)
    url = item_url(level, tree[level]["id"])

    assert client.put(url, json=body(level, group)).status_code == status
    assert client.delete(url).status_code == status
    below = _next_level_slot(level)
    if below is not None:
        child = JSON_LEVELS[JSON_LEVELS.index(level) + 1] if level != JSON_LEVELS[-1] else "Image"
        assert client.post(f"{url}/{SEGMENTS[child]}", json={}).status_code == status

    signin(client, CURATOR)
    assert client.get(url).status_code == 200


def test_a_study_can_only_be_created_in_a_group_the_caller_belongs_to(
    client: TestClient, group: int
) -> None:
    signin(client, OUTSIDER)
    assert client.post("/api/studies", json=body("Study", group)).status_code == 403
    signout(client)
    assert client.post("/api/studies", json=body("Study", group)).status_code == 401


def test_moving_a_study_takes_membership_of_both_groups(
    client: TestClient, group: int, tree: dict
) -> None:
    signin(client, OUTSIDER)
    theirs = make_group(client, "Their Lab")
    signin(client, CURATOR)
    url = item_url("Study", tree["Study"]["id"])

    assert client.put(url, json=body("Study", theirs)).status_code == 403
    assert client.get(url).json()["research_group"] == group

    mine = make_group(client, "My Other Lab")
    assert client.put(url, json=body("Study", mine)).status_code == 200
