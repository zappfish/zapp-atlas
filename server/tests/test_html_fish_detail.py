from __future__ import annotations

import re

from fastapi.testclient import TestClient

FISH = {"zfin_id": "ZFIN:ZDB-GENO-960809-7", "name": "AB"}


def _sign_in(client: TestClient, orcid_id: str = "0000-0002-1825-0097") -> None:
    client.app.state.settings.dev_auth = True
    client.post("/auth/dev/login", data={"name": "Ada", "orcid_id": orcid_id})


def _group_with_fish(client: TestClient) -> tuple[str, str]:
    group_path = client.post(
        "/research-groups", data={"name": "Detail Lab"}, follow_redirects=False
    ).headers["location"]
    client.post(f"{group_path}/fish-tank", data=FISH)
    # The detail link is "<id>-<zfin-slug>"; match the whole segment.
    detail_url = re.search(
        r'href="(/research-groups/\d+/fish-tank/\d+-[a-z0-9-]+)"',
        client.get(group_path).text,
    ).group(1)
    return group_path, detail_url


def test_fish_detail_shows_the_fish(client: TestClient) -> None:
    _sign_in(client)
    _, detail_url = _group_with_fish(client)

    res = client.get(detail_url)
    assert res.status_code == 200
    assert FISH["name"] in res.text
    assert "ZDB-GENO-960809-7" in res.text
    assert "Added on" in res.text


def test_fish_detail_serves_a_fragment_over_htmx(client: TestClient) -> None:
    _sign_in(client)
    _, detail_url = _group_with_fish(client)

    res = client.get(detail_url, headers={"HX-Request": "true"})
    assert res.status_code == 200
    assert "<!doctype" not in res.text.lower()
    assert 'id="dash-body"' in res.text


def test_unknown_fish_detail_404s(client: TestClient) -> None:
    _sign_in(client)
    group_path = client.post(
        "/research-groups", data={"name": "Empty"}, follow_redirects=False
    ).headers["location"]

    res = client.get(f"{group_path}/fish-tank/999999", follow_redirects=False)
    assert res.status_code == 404


def test_non_member_cannot_view_fish_detail(client: TestClient) -> None:
    _sign_in(client, orcid_id="0000-0001-1111-1111")
    _, detail_url = _group_with_fish(client)

    other = TestClient(client.app)
    other.app.state.settings.dev_auth = True
    other.post("/auth/dev/login", data={"name": "Bob", "orcid_id": "0000-0002-2222-2222"})

    res = other.get(detail_url, follow_redirects=False)
    assert res.status_code == 404
