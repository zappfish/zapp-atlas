"""Member display names (#142).

Adding someone to a group by ORCID used to leave nothing to show but the raw
CURIE until that person's first login. Now the add prefetches an
``OrcidIdentity`` row (name from ORCID's public API, best effort) and member
responses carry a ``name`` field joined from it.
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from test_api_cabinet_fish_tank import ADMIN, MEMBER, make_group, signin

from zapp_atlas.auth.models import OrcidIdentity


def _patch_public_name(monkeypatch, value: str | None) -> None:
    monkeypatch.setattr(
        "zapp_atlas.auth.services.fetch_orcid_public_name",
        lambda *args, **kwargs: value,
    )


def _add_member(client: TestClient, group_id: int, orcid: str) -> dict:
    signin(client, ADMIN)
    res = client.post(
        f"/api/research-groups/{group_id}/members",
        json={"member": orcid, "role": "member"},
    )
    assert res.status_code == 201, res.text
    return res.json()


def _members_by_orcid(client: TestClient, group_id: int) -> dict[str, dict]:
    res = client.get(f"/api/research-groups/{group_id}/members")
    assert res.status_code == 200
    return {m["member"]: m for m in res.json()}


def test_added_member_shows_public_name_before_first_login(client, monkeypatch) -> None:
    _patch_public_name(monkeypatch, "Divya Example")
    group_id = make_group(client)

    created = _add_member(client, group_id, MEMBER)
    assert created["name"] == "Divya Example"

    members = _members_by_orcid(client, group_id)
    assert members[f"ORCID:{MEMBER}"]["name"] == "Divya Example"


def test_failed_lookup_falls_back_to_null_name(client) -> None:
    # conftest's autouse stub makes every public-API lookup come back empty.
    group_id = make_group(client)

    created = _add_member(client, group_id, MEMBER)
    assert created["name"] is None

    members = _members_by_orcid(client, group_id)
    assert members[f"ORCID:{MEMBER}"]["name"] is None


def test_login_updates_prefetched_identity_without_duplicating(client, monkeypatch) -> None:
    _patch_public_name(monkeypatch, "Public Name")
    group_id = make_group(client)
    _add_member(client, group_id, MEMBER)

    # The person logs in themselves; their login name is authoritative.
    signin(client, MEMBER, name="Authoritative Name")

    signin(client, ADMIN)
    members = _members_by_orcid(client, group_id)
    assert members[f"ORCID:{MEMBER}"]["name"] == "Authoritative Name"

    with client.app.state.session_factory() as session:
        count = session.scalar(
            select(func.count()).select_from(OrcidIdentity).where(OrcidIdentity.orcid_id == MEMBER)
        )
    assert count == 1
