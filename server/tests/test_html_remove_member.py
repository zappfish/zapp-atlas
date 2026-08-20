from __future__ import annotations

import re

from fastapi.testclient import TestClient

from zapp_atlas.schema.sqla import ResearchGroupMember

ADMIN = "0000-0002-1825-0097"
OTHER = "0000-0001-1111-1111"


def _sign_in(client: TestClient, orcid_id: str) -> TestClient:
    client.app.state.settings.dev_auth = True
    client.post("/auth/dev/login", data={"name": "User", "orcid_id": orcid_id})
    return client


def _group_with_two_members(client: TestClient) -> str:
    group_path = client.post(
        "/research-groups", data={"name": "Remove Lab"}, follow_redirects=False
    ).headers["location"]
    client.post(f"{group_path}/members", data={"member": OTHER, "role": "member"})
    return group_path


def _other_remove_url(client: TestClient, group_path: str) -> str:
    # The only remove button on the page targets the other member (not self).
    return re.search(
        r'data-delete-url="(/research-groups/\d+/members/\d+/remove)"',
        client.get(group_path).text,
    ).group(1)


def test_admin_can_remove_another_member(client: TestClient) -> None:
    _sign_in(client, ADMIN)
    group_path = _group_with_two_members(client)

    res = client.post(_other_remove_url(client, group_path), follow_redirects=False)
    assert res.status_code == 303

    with client.app.state.session_factory() as session:
        remaining = session.query(ResearchGroupMember).all()
        assert len(remaining) == 1
        assert remaining[0].member == f"ORCID:{ADMIN}"


def test_no_remove_button_on_your_own_row(client: TestClient) -> None:
    _sign_in(client, ADMIN)
    group_path = _group_with_two_members(client)
    # Two members, but only one remove button — the admin cannot remove self.
    assert client.get(group_path).text.count('data-delete-url="/research-groups') == 1


def test_removing_yourself_is_forbidden(client: TestClient) -> None:
    _sign_in(client, ADMIN)
    group_path = _group_with_two_members(client)

    with client.app.state.session_factory() as session:
        my_id = (
            session.query(ResearchGroupMember)
            .filter_by(member=f"ORCID:{ADMIN}")
            .one()
            .id
        )
    res = client.post(f"{group_path}/members/{my_id}/remove", follow_redirects=False)
    assert res.status_code == 403


def test_non_admin_cannot_remove(client: TestClient) -> None:
    _sign_in(client, ADMIN)
    group_path = _group_with_two_members(client)
    remove_url = _other_remove_url(client, group_path)

    member = TestClient(client.app)
    _sign_in(member, OTHER)
    # The member row belongs to OTHER; they are not an admin.
    res = member.post(remove_url, follow_redirects=False)
    assert res.status_code == 403


def test_non_member_cannot_remove(client: TestClient) -> None:
    _sign_in(client, ADMIN)
    group_path = _group_with_two_members(client)
    remove_url = _other_remove_url(client, group_path)

    stranger = TestClient(client.app)
    _sign_in(stranger, "0000-0009-9999-9999")
    res = stranger.post(remove_url, follow_redirects=False)
    assert res.status_code == 404
