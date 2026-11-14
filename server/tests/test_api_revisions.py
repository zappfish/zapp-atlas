"""Every save beneath a study is recorded as a snapshot of the whole study."""

from fastapi.testclient import TestClient
from support import CURATOR, OUTSIDER, body, item_url, make_tree, signin, signout


def _revisions(client: TestClient, study_id: int) -> list[dict]:
    res = client.get(f"/api/studies/{study_id}/revisions")
    assert res.status_code == 200, res.text
    return res.json()


def _document(client: TestClient, study_id: int, version: int) -> dict:
    res = client.get(f"/api/studies/{study_id}/revisions/{version}")
    assert res.status_code == 200, res.text
    return res.json()["document"]


def test_each_save_adds_a_revision_saying_who_made_it(client: TestClient, tree: dict) -> None:
    study_id = tree["Study"]["id"]
    # One for the study, and one for each level created beneath it.
    revisions = _revisions(client, study_id)
    assert [r["version"] for r in revisions] == [1, 2, 3, 4]
    assert {r["saved_by"] for r in revisions} == {f"ORCID:{CURATOR}"}
    assert all(r["created_at"] for r in revisions)


def test_a_revision_holds_the_whole_study_as_it_stood(client: TestClient, tree: dict) -> None:
    study_id = tree["Study"]["id"]
    assert _document(client, study_id, 1)["experiment"] in (None, [])
    assert _document(client, study_id, 4) == client.get(item_url("Study", study_id)).json()


def test_a_save_deep_in_the_tree_is_a_revision_of_the_study(client: TestClient, tree: dict) -> None:
    study_id = tree["Study"]["id"]
    url = item_url("Experiment", tree["Experiment"]["id"])
    client.put(url, json={"rearing_condition_comment": "kept at 30 degrees"})

    [experiment] = _document(client, study_id, 5)["experiment"]
    assert experiment["rearing_condition_comment"] == "kept at 30 degrees"
    # And the earlier snapshot still says what was true then.
    [before] = _document(client, study_id, 4)["experiment"]
    assert before["rearing_condition_comment"] != "kept at 30 degrees"


def test_deleting_a_level_is_a_revision_without_it(client: TestClient, tree: dict) -> None:
    study_id = tree["Study"]["id"]
    client.delete(item_url("ExposureEvent", tree["ExposureEvent"]["id"]))

    [experiment] = _document(client, study_id, 5)["experiment"]
    assert experiment["exposure_event"] in (None, [])


def test_uploading_an_image_is_a_revision(client: TestClient, tree: dict) -> None:
    client.post(
        f"/api/observations/{tree['PhenotypeObservationSet']['id']}/images",
        files={"file": ("fish.png", b"a picture", "image/png")},
    )
    assert len(_revisions(client, tree["Study"]["id"])) == 5


def test_a_refused_save_leaves_no_revision(client: TestClient, group: int, tree: dict) -> None:
    study_id = tree["Study"]["id"]
    url = item_url("ExposureEvent", tree["ExposureEvent"]["id"])
    assert client.put(url, json={"stressor": [{}]}).status_code == 422

    client.post("/api/studies", json=body("Study", group) | {"nickname": "taken"})
    clash = client.put(
        item_url("Study", study_id), json=body("Study", group) | {"nickname": "taken"}
    )
    assert clash.status_code == 409

    assert len(_revisions(client, study_id)) == 4


def test_an_unknown_revision_is_a_404(client: TestClient, tree: dict) -> None:
    assert client.get(f"/api/studies/{tree['Study']['id']}/revisions/99").status_code == 404


def test_a_deleted_studys_history_goes_with_it(client: TestClient, group: int, tree: dict) -> None:
    study_id = tree["Study"]["id"]
    client.delete(item_url("Study", study_id))
    assert client.get(f"/api/studies/{study_id}/revisions").status_code == 404

    # A study created afterwards starts its own history from 1.
    again = client.post("/api/studies", json=body("Study", group)).json()
    assert [r["version"] for r in _revisions(client, again["id"])] == [1]


def test_the_history_of_a_draft_is_as_private_as_the_draft(client: TestClient, group: int) -> None:
    study_id = make_tree(client, group, status="draft")["Study"]["id"]
    assert len(_revisions(client, study_id)) == 4

    for who in (None, OUTSIDER):
        signout(client)
        if who is not None:
            signin(client, who)
        assert client.get(f"/api/studies/{study_id}/revisions").status_code == 404
        assert client.get(f"/api/studies/{study_id}/revisions/1").status_code == 404
