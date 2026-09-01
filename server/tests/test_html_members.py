from __future__ import annotations

from fastapi.testclient import TestClient

ADMIN = "0000-0002-1825-0097"
OTHER = "0000-0001-1111-1111"


def _sign_in(client: TestClient, orcid_id: str) -> TestClient:
    client.app.state.settings.dev_auth = True
    client.post("/auth/dev/login", data={"name": "User", "orcid_id": orcid_id})
    return client


def _new_group(client: TestClient) -> str:
    return client.post(
        "/research-groups", data={"name": "Members Lab"}, follow_redirects=False
    ).headers["location"]


def test_creator_is_listed_as_admin_and_sees_the_add_form(client: TestClient) -> None:
    _sign_in(client, ADMIN)
    page = client.get(_new_group(client)).text
    assert ADMIN in page
    assert "member__role--admin" in page
    assert "member-add" in page


def test_admin_can_add_a_member(client: TestClient) -> None:
    _sign_in(client, ADMIN)
    group_path = _new_group(client)

    res = client.post(
        f"{group_path}/members",
        data={"member": OTHER, "role": "member"},
        follow_redirects=False,
    )
    assert res.status_code == 303
    assert OTHER in client.get(group_path).text


def test_non_admin_sees_no_add_form_and_cannot_add(client: TestClient) -> None:
    _sign_in(client, ADMIN)
    group_path = _new_group(client)
    client.post(f"{group_path}/members", data={"member": OTHER, "role": "member"})

    member = TestClient(client.app)
    _sign_in(member, OTHER)

    page = member.get(group_path).text
    assert "members-modal" in page  # can see the list
    assert "member-add" not in page  # but not the add form

    res = member.post(
        f"{group_path}/members",
        data={"member": "0000-0003-3333-3333", "role": "member"},
        follow_redirects=False,
    )
    assert res.status_code == 403


def test_non_member_cannot_add(client: TestClient) -> None:
    _sign_in(client, ADMIN)
    group_path = _new_group(client)

    stranger = TestClient(client.app)
    _sign_in(stranger, "0000-0009-9999-9999")

    res = stranger.post(
        f"{group_path}/members",
        data={"member": OTHER, "role": "member"},
        follow_redirects=False,
    )
    assert res.status_code == 404


def test_add_rejects_a_bad_orcid(client: TestClient) -> None:
    _sign_in(client, ADMIN)
    group_path = _new_group(client)

    res = client.post(
        f"{group_path}/members",
        data={"member": "not-an-orcid", "role": "member"},
        follow_redirects=False,
    )
    assert res.status_code == 422
