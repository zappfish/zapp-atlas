from __future__ import annotations

from fastapi.testclient import TestClient

FISH = {"zfin_id": "ZFIN:ZDB-GENO-960809-7", "name": "AB"}


def _sign_in(client: TestClient, orcid_id: str = "0000-0002-1825-0097") -> None:
    client.app.state.settings.dev_auth = True
    client.post("/auth/dev/login", data={"name": "Ada", "orcid_id": orcid_id})


def _new_group(client: TestClient) -> str:
    res = client.post(
        "/research-groups", data={"name": "Fish Lab"}, follow_redirects=False
    )
    return res.headers["location"]  # /research-groups/{id}


def test_add_fish_appears_in_the_tank(client: TestClient) -> None:
    _sign_in(client)
    group_path = _new_group(client)

    res = client.post(f"{group_path}/fish-tank", data=FISH, follow_redirects=False)
    assert res.status_code == 303
    assert res.headers["location"] == group_path

    page = client.get(group_path)
    assert FISH["name"] in page.text
    assert "ZDB-GENO-960809-7" in page.text


def test_add_fish_over_htmx_redirects(client: TestClient) -> None:
    _sign_in(client)
    group_path = _new_group(client)

    res = client.post(
        f"{group_path}/fish-tank",
        data=FISH,
        headers={"HX-Request": "true"},
        follow_redirects=False,
    )
    assert res.status_code == 204
    assert res.headers["HX-Redirect"] == group_path


def test_add_fish_rejects_a_bad_zfin_id(client: TestClient) -> None:
    _sign_in(client)
    group_path = _new_group(client)

    res = client.post(
        f"{group_path}/fish-tank",
        data={"zfin_id": "not-a-zfin", "name": "X"},
        follow_redirects=False,
    )
    assert res.status_code == 422


def test_non_member_cannot_add_fish(client: TestClient) -> None:
    _sign_in(client, orcid_id="0000-0001-1111-1111")
    group_path = _new_group(client)

    other = TestClient(client.app)
    other.app.state.settings.dev_auth = True
    other.post("/auth/dev/login", data={"name": "Bob", "orcid_id": "0000-0002-2222-2222"})

    res = other.post(f"{group_path}/fish-tank", data=FISH, follow_redirects=False)
    assert res.status_code == 404
