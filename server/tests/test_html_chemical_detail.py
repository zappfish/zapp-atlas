from __future__ import annotations

import re

from fastapi.testclient import TestClient


def _sign_in(client: TestClient, orcid_id: str = "0000-0002-1825-0097") -> None:
    client.app.state.settings.dev_auth = True
    client.post("/auth/dev/login", data={"name": "Ada", "orcid_id": orcid_id})


def _group_with_chemical(client: TestClient) -> tuple[str, str]:
    group_path = client.post(
        "/research-groups", data={"name": "Cabinet Lab"}, follow_redirects=False
    ).headers["location"]
    client.post(f"{group_path}/chemical-cabinet", data={"chemical_id": "CHEBI:16236"})
    detail_url = re.search(
        r'href="(/research-groups/\d+/chemical-cabinet/\d+-[a-z0-9-]+)"',
        client.get(group_path).text,
    ).group(1)
    return group_path, detail_url


def test_chemical_detail_shows_the_chemical(client: TestClient) -> None:
    _sign_in(client)
    _, detail_url = _group_with_chemical(client)

    res = client.get(detail_url)
    assert res.status_code == 200
    assert "CHEBI:16236" in res.text
    assert "Added on" in res.text


def test_chemical_detail_serves_a_fragment_over_htmx(client: TestClient) -> None:
    _sign_in(client)
    _, detail_url = _group_with_chemical(client)

    res = client.get(detail_url, headers={"HX-Request": "true"})
    assert res.status_code == 200
    assert "<!doctype" not in res.text.lower()
    assert 'id="dash-body"' in res.text


def test_unknown_chemical_detail_404s(client: TestClient) -> None:
    _sign_in(client)
    group_path = client.post(
        "/research-groups", data={"name": "Empty"}, follow_redirects=False
    ).headers["location"]

    res = client.get(
        f"{group_path}/chemical-cabinet/999999", follow_redirects=False
    )
    assert res.status_code == 404


def test_non_member_cannot_view_chemical_detail(client: TestClient) -> None:
    _sign_in(client, orcid_id="0000-0001-1111-1111")
    _, detail_url = _group_with_chemical(client)

    other = TestClient(client.app)
    other.app.state.settings.dev_auth = True
    other.post("/auth/dev/login", data={"name": "Bob", "orcid_id": "0000-0002-2222-2222"})

    res = other.get(detail_url, follow_redirects=False)
    assert res.status_code == 404
