from __future__ import annotations

import re

from fastapi.testclient import TestClient

from zapp_atlas.schema.sqla import ChemicalCabinetEntry


def _sign_in(client: TestClient, orcid_id: str = "0000-0002-1825-0097") -> None:
    client.app.state.settings.dev_auth = True
    client.post("/auth/dev/login", data={"name": "Ada", "orcid_id": orcid_id})


def _group_with_chemical(client: TestClient) -> tuple[str, str]:
    group_path = client.post(
        "/research-groups", data={"name": "Edit Chem"}, follow_redirects=False
    ).headers["location"]
    client.post(f"{group_path}/chemical-cabinet", data={"chemical_id": "CHEBI:16236"})
    edit_url = re.search(
        r'data-edit-url="(/research-groups/\d+/chemical-cabinet/\d+/edit)"',
        client.get(group_path).text,
    ).group(1)
    return group_path, edit_url


def test_edit_changes_the_chemical_id(client: TestClient) -> None:
    _sign_in(client)
    group_path, edit_url = _group_with_chemical(client)

    res = client.post(
        edit_url, data={"chemical_id": "CHEBI:35456"}, follow_redirects=False
    )
    assert res.status_code == 303
    assert res.headers["location"] == group_path

    with client.app.state.session_factory() as session:
        entry = session.query(ChemicalCabinetEntry).one()
        assert entry.chemical_id == "CHEBI:35456"


def test_edit_prefills_the_current_value(client: TestClient) -> None:
    _sign_in(client)
    group_path, _ = _group_with_chemical(client)
    assert 'data-edit-value="CHEBI:16236"' in client.get(group_path).text


def test_edit_unknown_chemical_404s(client: TestClient) -> None:
    _sign_in(client)
    group_path = client.post(
        "/research-groups", data={"name": "Empty"}, follow_redirects=False
    ).headers["location"]

    res = client.post(
        f"{group_path}/chemical-cabinet/999999/edit",
        data={"chemical_id": "CHEBI:1"},
        follow_redirects=False,
    )
    assert res.status_code == 404


def test_non_member_cannot_edit_chemical(client: TestClient) -> None:
    _sign_in(client, orcid_id="0000-0001-1111-1111")
    _, edit_url = _group_with_chemical(client)

    other = TestClient(client.app)
    other.app.state.settings.dev_auth = True
    other.post("/auth/dev/login", data={"name": "Bob", "orcid_id": "0000-0002-2222-2222"})

    res = other.post(
        edit_url, data={"chemical_id": "CHEBI:1"}, follow_redirects=False
    )
    assert res.status_code == 404
