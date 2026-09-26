"""Member names on the research-group membership API (#142).

``ResearchGroupMember`` stores only an ORCID CURIE and a role; human names live
on ``OrcidIdentity``. These tests cover how names reach the membership
responses: from a member's own login, and — for members added by ORCID before
they ever sign in — from the ORCID public API via the app's name lookup
(``app.state.orcid_name_lookup``, stubbed out in the test client).
"""

from __future__ import annotations

from fastapi.testclient import TestClient

ADMIN = "0000-0002-1825-0097"
NEW_MEMBER = "0000-0001-1111-2222"


def signin(client: TestClient, orcid_id: str, name: str = "Test User") -> None:
    client.app.state.settings.dev_auth = True
    res = client.post(
        "/auth/dev/login",
        data={"orcid_id": orcid_id, "name": name},
        follow_redirects=False,
    )
    assert res.status_code in (303, 307)


def make_group(client: TestClient, name: str = "Test Lab") -> int:
    signin(client, ADMIN, name="Josiah Carberry")
    res = client.post("/api/research-groups", json={"name": name})
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_members_listing_names_a_member_who_has_logged_in(client: TestClient) -> None:
    group_id = make_group(client)
    members = client.get(f"/api/research-groups/{group_id}/members").json()
    assert members[0]["member"] == f"ORCID:{ADMIN}"
    assert members[0]["name"] == "Josiah Carberry"


def test_adding_a_member_prefetches_their_public_name(client: TestClient) -> None:
    group_id = make_group(client)
    client.app.state.orcid_name_lookup = lambda orcid_id: "Divya Example"

    res = client.post(
        f"/api/research-groups/{group_id}/members",
        json={"member": NEW_MEMBER, "role": "member"},
    )
    assert res.status_code == 201, res.text
    assert res.json()["name"] == "Divya Example"

    # The name is stored, not merely echoed: the listing (which resolves names
    # through OrcidIdentity) shows it before the member has ever logged in.
    members = client.get(f"/api/research-groups/{group_id}/members").json()
    by_orcid = {m["member"]: m["name"] for m in members}
    assert by_orcid[f"ORCID:{NEW_MEMBER}"] == "Divya Example"


def test_member_is_added_even_when_no_public_name_is_found(client: TestClient) -> None:
    # A private or unknown ORCID record yields no name; the add must still work.
    group_id = make_group(client)
    client.app.state.orcid_name_lookup = lambda orcid_id: None

    res = client.post(
        f"/api/research-groups/{group_id}/members",
        json={"member": NEW_MEMBER, "role": "member"},
    )
    assert res.status_code == 201, res.text
    assert res.json()["name"] is None


def test_adding_a_member_who_already_logged_in_keeps_their_login_name(
    client: TestClient,
) -> None:
    group_id = make_group(client)
    # They logged in themselves at some point: that name is authoritative.
    signin(client, NEW_MEMBER, name="Dr. Divya Example")

    lookups: list[str] = []

    def lookup(orcid_id: str) -> str:
        lookups.append(orcid_id)
        return "Stale Public Name"

    client.app.state.orcid_name_lookup = lookup
    signin(client, ADMIN, name="Josiah Carberry")
    res = client.post(
        f"/api/research-groups/{group_id}/members",
        json={"member": NEW_MEMBER, "role": "member"},
    )
    assert res.status_code == 201, res.text
    assert res.json()["name"] == "Dr. Divya Example"
    assert lookups == []  # no pointless network call for a known identity


def test_login_name_replaces_the_prefetched_public_name(client: TestClient) -> None:
    group_id = make_group(client)
    client.app.state.orcid_name_lookup = lambda orcid_id: "D. Example"
    res = client.post(
        f"/api/research-groups/{group_id}/members",
        json={"member": NEW_MEMBER, "role": "member"},
    )
    assert res.json()["name"] == "D. Example"

    # The member signs in themselves; their own login name is authoritative.
    signin(client, NEW_MEMBER, name="Divya Example")
    members = client.get(f"/api/research-groups/{group_id}/members").json()
    by_orcid = {m["member"]: m["name"] for m in members}
    assert by_orcid[f"ORCID:{NEW_MEMBER}"] == "Divya Example"
