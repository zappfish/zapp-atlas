from __future__ import annotations

from fastapi.testclient import TestClient

FISH = {"zfin_id": "ZFIN:ZDB-GENO-960809-7", "name": "AB"}


def _sign_in(client: TestClient) -> None:
    client.app.state.settings.dev_auth = True
    client.post("/auth/dev/login", data={"name": "Ada", "orcid_id": "0000-0002-1825-0097"})


def _new_group(client: TestClient) -> str:
    return client.post(
        "/research-groups", data={"name": "Dup Lab"}, follow_redirects=False
    ).headers["location"]


def test_duplicate_chemical_redirects_with_a_notice(client: TestClient) -> None:
    _sign_in(client)
    group_path = _new_group(client)
    client.post(f"{group_path}/chemical-cabinet", data={"chemical_id": "CHEBI:16236"})

    res = client.post(
        f"{group_path}/chemical-cabinet",
        data={"chemical_id": "CHEBI:16236"},
        follow_redirects=False,
    )
    # A duplicate is a benign conflict: redirect, not a raw 409 JSON page.
    assert res.status_code == 303
    assert "notice=" in res.headers["location"]

    page = client.get(res.headers["location"])
    assert "Chemical already exists in this research group" in page.text
    assert '{"detail"' not in page.text


def test_duplicate_fish_redirects_with_a_notice(client: TestClient) -> None:
    _sign_in(client)
    group_path = _new_group(client)
    client.post(f"{group_path}/fish-tank", data=FISH)

    res = client.post(
        f"{group_path}/fish-tank", data=FISH, follow_redirects=False
    )
    assert res.status_code == 303
    assert "notice=" in res.headers["location"]
    assert "already in this tank" in client.get(res.headers["location"]).text
