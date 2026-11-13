"""Images: a file uploaded beneath an observation, and a row describing it."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sampling import sample
from support import OUTSIDER, comparable, item_url, signin, signout

PNG = b"\x89PNG\r\n\x1a\n not really a picture"


def _upload(client: TestClient, observation_id: int, **fields: str):
    return client.post(
        f"/api/observations/{observation_id}/images",
        files={"file": ("fish.png", PNG, "image/png")},
        data=fields,
    )


@pytest.fixture
def image(client: TestClient, tree: dict) -> dict:
    res = _upload(client, tree["PhenotypeObservationSet"]["id"], **sample("Image", full=True))
    assert res.status_code == 201, res.text
    return res.json()


def _stored_files(client: TestClient) -> list[Path]:
    return [p for p in Path(client.app.state.settings.upload_dir).rglob("*") if p.is_file()]


def test_an_upload_stores_the_file_and_every_field_describing_it(
    client: TestClient, tree: dict, image: dict
) -> None:
    assert comparable(image) == sample("Image", full=True)

    fetched = client.get(item_url("Image", image["id"]))
    assert fetched.content == PNG
    assert fetched.headers["content-type"] == "image/png"

    observation = client.get(
        item_url("PhenotypeObservationSet", tree["PhenotypeObservationSet"]["id"])
    )
    assert [listed["id"] for listed in observation.json()["image"]] == [image["id"]]


def test_an_images_description_can_be_replaced(client: TestClient, image: dict) -> None:
    res = client.put(item_url("Image", image["id"]), json={"magnification": "40x"})
    assert res.status_code == 200
    assert comparable(res.json()) == {
        "magnification": "40x",
        "resolution": None,
        "scale_bar": None,
        "image_scope": None,
    }
    assert client.get(item_url("Image", image["id"])).content == PNG


def test_saving_an_observation_keeps_its_images(
    client: TestClient, tree: dict, image: dict
) -> None:
    url = item_url("PhenotypeObservationSet", tree["PhenotypeObservationSet"]["id"])
    assert client.put(url, json={}).status_code == 200
    assert [listed["id"] for listed in client.get(url).json()["image"]] == [image["id"]]
    assert client.get(item_url("Image", image["id"])).content == PNG


def test_deleting_an_image_deletes_its_file(client: TestClient, image: dict) -> None:
    assert _stored_files(client)
    assert client.delete(item_url("Image", image["id"])).status_code == 204
    assert client.get(item_url("Image", image["id"])).status_code == 404
    assert not _stored_files(client)


def test_deleting_a_study_deletes_the_files_of_its_images(
    client: TestClient, tree: dict, image: dict
) -> None:
    assert client.delete(item_url("Study", tree["Study"]["id"])).status_code == 204
    assert not _stored_files(client)


def test_only_images_are_accepted(client: TestClient, tree: dict) -> None:
    res = client.post(
        f"/api/observations/{tree['PhenotypeObservationSet']['id']}/images",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert res.status_code == 415


def test_an_oversized_file_is_refused(client: TestClient, tree: dict) -> None:
    client.app.state.settings.max_upload_bytes = 4
    assert _upload(client, tree["PhenotypeObservationSet"]["id"]).status_code == 413
    assert not _stored_files(client)


def test_an_unknown_field_is_refused(client: TestClient, tree: dict) -> None:
    assert _upload(client, tree["PhenotypeObservationSet"]["id"], colour="red").status_code == 422


@pytest.mark.parametrize(("who", "status"), [(None, 401), (OUTSIDER, 403)])
def test_only_a_member_may_change_images(
    client: TestClient, tree: dict, image: dict, who: str | None, status: int
) -> None:
    signout(client)
    if who is not None:
        signin(client, who)
    assert _upload(client, tree["PhenotypeObservationSet"]["id"]).status_code == status
    assert client.put(item_url("Image", image["id"]), json={}).status_code == status
    assert client.delete(item_url("Image", image["id"])).status_code == status
    assert client.get(item_url("Image", image["id"])).status_code == 200
