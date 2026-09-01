from __future__ import annotations

import re

from fastapi.testclient import TestClient

from zapp_atlas.schema.sqla import ChemicalCabinetEntry


def _sign_in(client: TestClient, orcid_id: str = "0000-0002-1825-0097") -> None:
    client.app.state.settings.dev_auth = True
    client.post("/auth/dev/login", data={"name": "Ada", "orcid_id": orcid_id})


def _group_with_chemical(client: TestClient) -> tuple[str, str]:
    group_path = client.post(
        "/research-groups", data={"name": "Del Chem"}, follow_redirects=False
    ).headers["location"]
    client.post(f"{group_path}/chemical-cabinet", data={"chemical_id": "CHEBI:16236"})
    delete_url = re.search(
        r'data-delete-url="(/research-groups/\d+/chemical-cabinet/\d+/delete)"',
        client.get(group_path).text,
    ).group(1)
    return group_path, delete_url


def test_delete_removes_the_chemical(client: TestClient) -> None:
    _sign_in(client)
    group_path, delete_url = _group_with_chemical(client)

    res = client.post(delete_url, follow_redirects=False)
    assert res.status_code == 303
    assert res.headers["location"] == group_path

    with client.app.state.session_factory() as session:
        assert session.query(ChemicalCabinetEntry).count() == 0


def test_delete_unknown_chemical_404s(client: TestClient) -> None:
    _sign_in(client)
    group_path = client.post(
        "/research-groups", data={"name": "Empty"}, follow_redirects=False
    ).headers["location"]

    res = client.post(
        f"{group_path}/chemical-cabinet/999999/delete", follow_redirects=False
    )
    assert res.status_code == 404


def test_non_member_cannot_delete_chemical(client: TestClient) -> None:
    _sign_in(client, orcid_id="0000-0001-1111-1111")
    _, delete_url = _group_with_chemical(client)

    other = TestClient(client.app)
    other.app.state.settings.dev_auth = True
    other.post("/auth/dev/login", data={"name": "Bob", "orcid_id": "0000-0002-2222-2222"})

    res = other.post(delete_url, follow_redirects=False)
    assert res.status_code == 404
