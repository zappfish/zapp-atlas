"""API tests for research groups, chemical cabinet, and fish tank.

Covers the authorization matrix (signed-out / outsider / member / admin), the
unique-grain 409s, cross-group isolation, fish get-or-create, and the
hand-written boundary shape (path-derived research_group; audit timestamps in
responses).
"""

from __future__ import annotations

from fastapi.testclient import TestClient

ADMIN = "0000-0002-1825-0097"
MEMBER = "0000-0001-1111-2222"
OUTSIDER = "0000-0003-3333-4444"

ETHANOL = "CHEBI:16236"
BPA = "CHEBI:33216"
AB_LINE = "ZFIN:ZDB-GENO-960809-7"
TU_LINE = "ZFIN:ZDB-GENO-990623-3"


def signin(client: TestClient, orcid_id: str, name: str = "Test User") -> None:
    client.app.state.settings.dev_auth = True
    res = client.post(
        "/auth/dev/login",
        data={"orcid_id": orcid_id, "name": name},
        follow_redirects=False,
    )
    assert res.status_code in (303, 307)


def signout(client: TestClient) -> None:
    client.cookies.clear()


def make_group(client: TestClient, name: str = "Test Lab") -> int:
    """Create a group as ADMIN (who becomes its admin) and return its id."""
    signin(client, ADMIN)
    res = client.post("/api/research-groups", json={"name": name})
    assert res.status_code == 201, res.text
    return res.json()["id"]


def add_member(client: TestClient, group_id: int, orcid: str, role: str) -> None:
    signin(client, ADMIN)
    res = client.post(
        f"/api/research-groups/{group_id}/members",
        json={"member": orcid, "role": role},
    )
    assert res.status_code == 201, res.text


# --------------------------------------------------------------------------- #
# Groups + membership
# --------------------------------------------------------------------------- #


def test_group_creator_becomes_admin_member(client: TestClient) -> None:
    group_id = make_group(client)
    res = client.get(f"/api/research-groups/{group_id}/members")
    assert res.status_code == 200
    members = res.json()
    assert len(members) == 1
    assert members[0]["member"] == f"ORCID:{ADMIN}"
    assert members[0]["role"] == "admin"


def test_list_my_groups_only_returns_groups_i_belong_to(client: TestClient) -> None:
    group_id = make_group(client, "Lab A")
    signin(client, OUTSIDER)
    assert client.get("/api/research-groups").json() == []
    signin(client, ADMIN)
    ids = [g["id"] for g in client.get("/api/research-groups").json()]
    assert ids == [group_id]


def test_only_admin_can_add_members(client: TestClient) -> None:
    group_id = make_group(client)
    add_member(client, group_id, MEMBER, "member")

    # A plain member may not add others.
    signin(client, MEMBER)
    res = client.post(
        f"/api/research-groups/{group_id}/members",
        json={"member": OUTSIDER, "role": "member"},
    )
    assert res.status_code == 403


def test_duplicate_member_is_conflict(client: TestClient) -> None:
    group_id = make_group(client)
    add_member(client, group_id, MEMBER, "member")
    signin(client, ADMIN)
    res = client.post(
        f"/api/research-groups/{group_id}/members",
        json={"member": MEMBER, "role": "admin"},
    )
    assert res.status_code == 409


def _member_id(client: TestClient, group_id: int, orcid: str) -> int:
    signin(client, ADMIN)
    members = client.get(f"/api/research-groups/{group_id}/members").json()
    return next(m["id"] for m in members if m["member"] == f"ORCID:{orcid}")


def test_admin_can_remove_member(client: TestClient) -> None:
    group_id = make_group(client)
    add_member(client, group_id, MEMBER, "member")
    member_id = _member_id(client, group_id, MEMBER)
    signin(client, ADMIN)
    assert client.delete(f"/api/research-groups/{group_id}/members/{member_id}").status_code == 204
    remaining = client.get(f"/api/research-groups/{group_id}/members").json()
    assert all(m["id"] != member_id for m in remaining)


def test_remove_unknown_member_is_404(client: TestClient) -> None:
    group_id = make_group(client)
    signin(client, ADMIN)
    res = client.delete(f"/api/research-groups/{group_id}/members/99999")
    assert res.status_code == 404


def test_only_admin_can_remove_members(client: TestClient) -> None:
    group_id = make_group(client)
    add_member(client, group_id, MEMBER, "member")
    member_id = _member_id(client, group_id, MEMBER)
    signin(client, MEMBER)  # a plain member may not remove anyone
    res = client.delete(f"/api/research-groups/{group_id}/members/{member_id}")
    assert res.status_code == 403


def test_admin_can_change_a_members_role(client: TestClient) -> None:
    group_id = make_group(client)
    add_member(client, group_id, MEMBER, "member")
    member_id = _member_id(client, group_id, MEMBER)
    signin(client, ADMIN)
    res = client.patch(
        f"/api/research-groups/{group_id}/members/{member_id}",
        json={"role": "admin"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["role"] == "admin"
    # the promotion is durable, and the row keeps its identity
    listed = client.get(f"/api/research-groups/{group_id}/members").json()
    promoted = next(m for m in listed if m["id"] == member_id)
    assert promoted["role"] == "admin"
    assert promoted["member"] == f"ORCID:{MEMBER}"


def test_promoted_member_can_then_manage_membership(client: TestClient) -> None:
    """The role change is real, not just a stored string."""
    group_id = make_group(client)
    add_member(client, group_id, MEMBER, "member")
    member_id = _member_id(client, group_id, MEMBER)
    signin(client, MEMBER)
    assert (
        client.post(
            f"/api/research-groups/{group_id}/members",
            json={"member": OUTSIDER, "role": "member"},
        ).status_code
        == 403
    )
    signin(client, ADMIN)
    client.patch(f"/api/research-groups/{group_id}/members/{member_id}", json={"role": "admin"})
    signin(client, MEMBER)
    assert (
        client.post(
            f"/api/research-groups/{group_id}/members",
            json={"member": OUTSIDER, "role": "member"},
        ).status_code
        == 201
    )


def test_patch_role_touches_updated_at(client: TestClient) -> None:
    group_id = make_group(client)
    add_member(client, group_id, MEMBER, "member")
    member_id = _member_id(client, group_id, MEMBER)
    signin(client, ADMIN)
    before = next(
        m
        for m in client.get(f"/api/research-groups/{group_id}/members").json()
        if m["id"] == member_id
    )
    after = client.patch(
        f"/api/research-groups/{group_id}/members/{member_id}",
        json={"role": "admin"},
    ).json()
    assert after["created_at"] == before["created_at"]
    assert after["updated_at"] > before["updated_at"]


def test_only_admin_can_change_roles(client: TestClient) -> None:
    group_id = make_group(client)
    add_member(client, group_id, MEMBER, "member")
    member_id = _member_id(client, group_id, MEMBER)
    signin(client, MEMBER)  # a plain member may not hand themselves admin
    res = client.patch(
        f"/api/research-groups/{group_id}/members/{member_id}", json={"role": "admin"}
    )
    assert res.status_code == 403


def test_patch_role_requires_authentication(client: TestClient) -> None:
    group_id = make_group(client)
    add_member(client, group_id, MEMBER, "member")
    member_id = _member_id(client, group_id, MEMBER)
    signout(client)
    res = client.patch(
        f"/api/research-groups/{group_id}/members/{member_id}", json={"role": "admin"}
    )
    assert res.status_code == 401


def test_patch_unknown_member_is_404(client: TestClient) -> None:
    group_id = make_group(client)
    signin(client, ADMIN)
    res = client.patch(f"/api/research-groups/{group_id}/members/99999", json={"role": "admin"})
    assert res.status_code == 404


def test_patch_member_from_another_group_is_404(client: TestClient) -> None:
    """A membership id is only addressable under the group that owns it."""
    mine = make_group(client, "Mine")
    theirs = make_group(client, "Theirs")
    add_member(client, theirs, MEMBER, "member")
    foreign_id = _member_id(client, theirs, MEMBER)
    signin(client, ADMIN)
    res = client.patch(f"/api/research-groups/{mine}/members/{foreign_id}", json={"role": "member"})
    assert res.status_code == 404


def test_patch_rejects_unknown_role(client: TestClient) -> None:
    group_id = make_group(client)
    add_member(client, group_id, MEMBER, "member")
    member_id = _member_id(client, group_id, MEMBER)
    signin(client, ADMIN)
    res = client.patch(
        f"/api/research-groups/{group_id}/members/{member_id}",
        json={"role": "superuser"},
    )
    assert res.status_code == 422


# --------------------------------------------------------------------------- #
# A group must always keep an admin
# --------------------------------------------------------------------------- #


def test_last_admin_cannot_demote_themselves(client: TestClient) -> None:
    group_id = make_group(client)
    add_member(client, group_id, MEMBER, "member")
    admin_id = _member_id(client, group_id, ADMIN)
    signin(client, ADMIN)
    res = client.patch(
        f"/api/research-groups/{group_id}/members/{admin_id}", json={"role": "member"}
    )
    assert res.status_code == 409
    still_admin = next(
        m
        for m in client.get(f"/api/research-groups/{group_id}/members").json()
        if m["id"] == admin_id
    )
    assert still_admin["role"] == "admin"


def test_last_admin_cannot_be_removed(client: TestClient) -> None:
    group_id = make_group(client)
    add_member(client, group_id, MEMBER, "member")
    admin_id = _member_id(client, group_id, ADMIN)
    signin(client, ADMIN)
    res = client.delete(f"/api/research-groups/{group_id}/members/{admin_id}")
    assert res.status_code == 409
    assert any(
        m["id"] == admin_id for m in client.get(f"/api/research-groups/{group_id}/members").json()
    )


def test_admin_may_step_down_once_another_admin_exists(client: TestClient) -> None:
    """The intended hand-over: promote a successor first, then demote yourself."""
    group_id = make_group(client)
    add_member(client, group_id, MEMBER, "member")
    successor_id = _member_id(client, group_id, MEMBER)
    admin_id = _member_id(client, group_id, ADMIN)
    signin(client, ADMIN)
    assert (
        client.patch(
            f"/api/research-groups/{group_id}/members/{successor_id}",
            json={"role": "admin"},
        ).status_code
        == 200
    )
    res = client.patch(
        f"/api/research-groups/{group_id}/members/{admin_id}", json={"role": "member"}
    )
    assert res.status_code == 200
    assert res.json()["role"] == "member"


def test_admin_may_leave_once_another_admin_exists(client: TestClient) -> None:
    group_id = make_group(client)
    add_member(client, group_id, MEMBER, "admin")
    admin_id = _member_id(client, group_id, ADMIN)
    signin(client, ADMIN)
    assert client.delete(f"/api/research-groups/{group_id}/members/{admin_id}").status_code == 204


def test_sole_admin_of_a_one_person_group_is_still_protected(
    client: TestClient,
) -> None:
    """No members to promote is not a licence to orphan the group."""
    group_id = make_group(client)
    admin_id = _member_id(client, group_id, ADMIN)
    signin(client, ADMIN)
    assert client.delete(f"/api/research-groups/{group_id}/members/{admin_id}").status_code == 409


def test_last_admin_guard_is_per_group(client: TestClient) -> None:
    """Another group's admins don't count toward this group's quorum."""
    mine = make_group(client, "Mine")
    make_group(client, "Theirs")  # ADMIN is also an admin over here
    add_member(client, mine, MEMBER, "member")
    admin_id = _member_id(client, mine, ADMIN)
    signin(client, ADMIN)
    res = client.patch(f"/api/research-groups/{mine}/members/{admin_id}", json={"role": "member"})
    assert res.status_code == 409


def test_demoting_a_plain_member_is_unaffected_by_the_guard(
    client: TestClient,
) -> None:
    """A no-op role write on a non-admin must not trip the admin quorum check."""
    group_id = make_group(client)
    add_member(client, group_id, MEMBER, "member")
    member_id = _member_id(client, group_id, MEMBER)
    signin(client, ADMIN)
    res = client.patch(
        f"/api/research-groups/{group_id}/members/{member_id}", json={"role": "member"}
    )
    assert res.status_code == 200
    assert res.json()["role"] == "member"


# --------------------------------------------------------------------------- #
# Authorization matrix (exercised through the cabinet)
# --------------------------------------------------------------------------- #


def test_cabinet_requires_authentication(client: TestClient) -> None:
    group_id = make_group(client)
    signout(client)
    res = client.get(f"/api/research-groups/{group_id}/chemical-cabinet")
    assert res.status_code == 401


def test_cabinet_hidden_from_non_members(client: TestClient) -> None:
    # Non-members get the same 404 as a missing group — group membership is
    # private, so existence isn't revealed to outsiders.
    group_id = make_group(client)
    signin(client, OUTSIDER)
    res = client.get(f"/api/research-groups/{group_id}/chemical-cabinet")
    assert res.status_code == 404


def test_unknown_group_is_404(client: TestClient) -> None:
    make_group(client)
    signin(client, ADMIN)
    res = client.get("/api/research-groups/99999/chemical-cabinet")
    assert res.status_code == 404


# --------------------------------------------------------------------------- #
# Chemical cabinet
# --------------------------------------------------------------------------- #


def test_member_can_add_and_read_cabinet_entries(client: TestClient) -> None:
    group_id = make_group(client)
    add_member(client, group_id, MEMBER, "member")
    signin(client, MEMBER)

    created = client.post(
        f"/api/research-groups/{group_id}/chemical-cabinet",
        json={"chemical_id": ETHANOL},
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["chemical_id"] == ETHANOL
    # Boundary shape: audit timestamps are exposed.
    assert body["created_at"] is not None
    assert body["updated_at"] is not None

    listed = client.get(f"/api/research-groups/{group_id}/chemical-cabinet").json()
    assert [e["chemical_id"] for e in listed] == [ETHANOL]


def test_cabinet_grain_conflict(client: TestClient) -> None:
    group_id = make_group(client)
    signin(client, ADMIN)
    url = f"/api/research-groups/{group_id}/chemical-cabinet"
    assert client.post(url, json={"chemical_id": ETHANOL}).status_code == 201
    assert client.post(url, json={"chemical_id": ETHANOL}).status_code == 409


def test_cabinet_entry_isolated_across_groups(client: TestClient) -> None:
    group_a = make_group(client, "Lab A")
    group_b = make_group(client, "Lab B")  # ADMIN is in both
    signin(client, ADMIN)
    a = client.post(
        f"/api/research-groups/{group_a}/chemical-cabinet", json={"chemical_id": ETHANOL}
    )
    b = client.post(
        f"/api/research-groups/{group_b}/chemical-cabinet", json={"chemical_id": ETHANOL}
    )
    # The grain is (group, chemical), so two groups may both stock ethanol.
    assert a.status_code == 201 and b.status_code == 201
    # But group B can't read group A's entry by id — 404, not a peek.
    entry_id = a.json()["id"]
    res = client.get(f"/api/research-groups/{group_b}/chemical-cabinet/{entry_id}")
    assert res.status_code == 404


def test_cabinet_patch_updates_chemical(client: TestClient) -> None:
    group_id = make_group(client)
    signin(client, ADMIN)
    url = f"/api/research-groups/{group_id}/chemical-cabinet"
    entry_id = client.post(url, json={"chemical_id": ETHANOL}).json()["id"]
    res = client.patch(f"{url}/{entry_id}", json={"chemical_id": BPA})
    assert res.status_code == 200
    assert res.json()["chemical_id"] == BPA


def test_cabinet_patch_unknown_entry_is_404(client: TestClient) -> None:
    group_id = make_group(client)
    signin(client, ADMIN)
    res = client.patch(
        f"/api/research-groups/{group_id}/chemical-cabinet/99999",
        json={"chemical_id": BPA},
    )
    assert res.status_code == 404


def test_cabinet_patch_into_existing_grain_conflicts(client: TestClient) -> None:
    group_id = make_group(client)
    signin(client, ADMIN)
    url = f"/api/research-groups/{group_id}/chemical-cabinet"
    client.post(url, json={"chemical_id": ETHANOL})
    bpa_id = client.post(url, json={"chemical_id": BPA}).json()["id"]
    # Patching BPA -> ETHANOL collides with the existing (group, ethanol) row.
    res = client.patch(f"{url}/{bpa_id}", json={"chemical_id": ETHANOL})
    assert res.status_code == 409


def test_cabinet_delete(client: TestClient) -> None:
    group_id = make_group(client)
    signin(client, ADMIN)
    url = f"/api/research-groups/{group_id}/chemical-cabinet"
    entry_id = client.post(url, json={"chemical_id": ETHANOL}).json()["id"]
    assert client.delete(f"{url}/{entry_id}").status_code == 204
    assert client.get(f"{url}/{entry_id}").status_code == 404


# --------------------------------------------------------------------------- #
# Fish tank
# --------------------------------------------------------------------------- #


def test_tank_add_get_or_creates_fish(client: TestClient) -> None:
    group_id = make_group(client)
    signin(client, ADMIN)
    created = client.post(
        f"/api/research-groups/{group_id}/fish-tank",
        json={"fish": {"zfin_id": AB_LINE, "name": "AB"}},
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["fish"] == {"zfin_id": AB_LINE, "name": "AB"}
    assert body["created_at"] is not None


def test_tank_grain_conflict(client: TestClient) -> None:
    group_id = make_group(client)
    signin(client, ADMIN)
    url = f"/api/research-groups/{group_id}/fish-tank"
    fish = {"fish": {"zfin_id": AB_LINE, "name": "AB"}}
    assert client.post(url, json=fish).status_code == 201
    assert client.post(url, json=fish).status_code == 409


def test_tank_rejects_malformed_zfin_id(client: TestClient) -> None:
    group_id = make_group(client)
    signin(client, ADMIN)
    res = client.post(
        f"/api/research-groups/{group_id}/fish-tank",
        json={"fish": {"zfin_id": "not-a-zfin", "name": "Mystery"}},
    )
    assert res.status_code == 422


def test_two_groups_may_tank_the_same_fish(client: TestClient) -> None:
    # The second entry reuses the existing Fish row rather than re-creating it.
    group_a = make_group(client, "Lab A")
    group_b = make_group(client, "Lab B")
    signin(client, ADMIN)
    fish = {"fish": {"zfin_id": AB_LINE, "name": "AB"}}
    a = client.post(f"/api/research-groups/{group_a}/fish-tank", json=fish)
    b = client.post(f"/api/research-groups/{group_b}/fish-tank", json=fish)
    assert a.status_code == 201 and b.status_code == 201
