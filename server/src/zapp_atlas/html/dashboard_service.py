"""Data assembly for the research group dashboard pages.

Gathers a group's fish tank, chemical cabinet, and members from the group-scoped
services and shapes them for the templates, keeping the HTML routes thin.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from zapp_atlas.auth.models import OrcidIdentity

_ORCID_PREFIX = "ORCID:"


def _record_slug(entry_id: int, label: str) -> str:
    """A readable path segment "<id>-<label>": the id (which the route reads
    back) followed by a slugified label for legibility. Only the leading id is
    significant; the rest is cosmetic.
    """
    slug = label.split(":", 1)[-1].lower().replace(" ", "-")
    return f"{entry_id}-{slug}"


def membership(session: Session, identity, group_id: int):
    """The caller's membership row, or None. Unknown group and non-membership
    both read as None, so a caller can't probe which groups exist.
    """
    from zapp_atlas.api.authz import orcid_curie
    from zapp_atlas.schema.sqla import ResearchGroup, ResearchGroupMember

    if session.get(ResearchGroup, group_id) is None:
        return None
    return (
        session.query(ResearchGroupMember)
        .filter_by(research_group=group_id, member=orcid_curie(identity.orcid_id))
        .one_or_none()
    )


def _initials(name: str | None) -> str:
    # Up to two initials from a name, for the avatar; a placeholder otherwise.
    if not name:
        return "?"
    parts = name.split()
    letters = parts[0][:1] + (parts[-1][:1] if len(parts) > 1 else "")
    return letters.upper()


def _member_names(session: Session, members) -> dict[str, str]:
    """Map each membership's ORCID CURIE to the person's name, for members who
    have signed in. A member added by ORCID but never signed in has no identity
    row, so their CURIE is absent and the caller falls back to the id.
    """
    bare_ids = [member.member.removeprefix(_ORCID_PREFIX) for member in members]
    if not bare_ids:
        return {}
    identities = (
        session.query(OrcidIdentity)
        .filter(OrcidIdentity.orcid_id.in_(bare_ids))
        .all()
    )
    return {
        _ORCID_PREFIX + identity.orcid_id: identity.name
        for identity in identities
        if identity.name
    }


def group_view(session: Session, identity, group_id: int) -> dict | None:
    """The dashboard context for a group, or None if the caller is not a
    member.
    """
    from zapp_atlas.api.authz import ResearchGroupRoleEnum
    from zapp_atlas.api.services import cabinet, fish_tank, research_groups
    from zapp_atlas.schema.sqla import ResearchGroup

    my_membership = membership(session, identity, group_id)
    if my_membership is None:
        return None
    group = session.get(ResearchGroup, group_id)
    is_admin = my_membership.role == ResearchGroupRoleEnum.admin.value

    tank = fish_tank.list_entries(session, group_id)
    chemicals = cabinet.list_entries(session, group_id)
    groups = research_groups.list_groups_for(session, identity)
    members = research_groups.list_members(session, group_id)
    names = _member_names(session, members)
    return {
        "groups": groups,
        "my_submissions_count": 0,
        "is_admin": is_admin,
        "members": [
            {
                "orcid": member.member.removeprefix(_ORCID_PREFIX),
                "role": member.role,
                "name": names.get(member.member),
                "initials": _initials(names.get(member.member)),
                # No self-removal: an admin can drop others, not their own seat.
                "remove_url": (
                    f"/research-groups/{group_id}/members/{member.id}/remove"
                    if member.id != my_membership.id
                    else None
                ),
            }
            for member in members
        ],
        "group": {
            "id": group.id,
            "name": group.name,
            "is_default": False,
            "chemical_count": len(chemicals),
            "fish_line_count": len(tank),
            "submission_count": 0,
        },
        "fish_tank": [
            {
                "name": entry.fish.name,
                "zf_id": entry.fish.zfin_id,
                "detail_url": (
                    "/research-groups/"
                    f"{group_id}/fish-tank/"
                    f"{_record_slug(entry.id, entry.fish.zfin_id)}"
                ),
                "delete_url": (
                    f"/research-groups/{group_id}/fish-tank/{entry.id}/delete"
                ),
            }
            for entry in tank
        ],
        "cabinet": [
            {
                "chemical_id": entry.chemical_id,
                "detail_url": (
                    "/research-groups/"
                    f"{group_id}/chemical-cabinet/"
                    f"{_record_slug(entry.id, entry.chemical_id)}"
                ),
                "edit_url": (
                    f"/research-groups/{group_id}/chemical-cabinet/{entry.id}/edit"
                ),
                "delete_url": (
                    f"/research-groups/{group_id}/chemical-cabinet/{entry.id}/delete"
                ),
            }
            for entry in chemicals
        ],
        "submissions": [],
    }


def _detail_shell(session: Session, identity, group_id: int) -> dict | None:
    """The sidebar and group context a record detail page needs, or None if the
    caller is not a member.
    """
    from zapp_atlas.api.services import research_groups
    from zapp_atlas.schema.sqla import ResearchGroup

    if membership(session, identity, group_id) is None:
        return None
    group = session.get(ResearchGroup, group_id)
    return {
        "groups": research_groups.list_groups_for(session, identity),
        "my_submissions_count": 0,
        "group": {"id": group.id, "name": group.name},
    }


def fish_detail_view(
    session: Session, identity, group_id: int, entry_id: int
) -> dict | None:
    """One fish tank entry with its group, or None if the caller is not a
    member or the entry is not in this group.
    """
    from zapp_atlas.api.services import fish_tank

    shell = _detail_shell(session, identity, group_id)
    if shell is None:
        return None
    entry = fish_tank.get_entry(session, group_id, entry_id)
    if entry is None:
        return None

    return shell | {
        "fish": {
            "name": entry.fish.name,
            "zf_id": entry.fish.zfin_id,
            "added_on": entry.created_at,
        },
    }


def chemical_detail_view(
    session: Session, identity, group_id: int, entry_id: int
) -> dict | None:
    """One chemical cabinet entry with its group, or None if the caller is not
    a member or the entry is not in this group.
    """
    from zapp_atlas.api.services import cabinet

    shell = _detail_shell(session, identity, group_id)
    if shell is None:
        return None
    entry = cabinet.get_entry(session, group_id, entry_id)
    if entry is None:
        return None

    return shell | {
        "chemical": {
            "chemical_id": entry.chemical_id,
            "added_on": entry.created_at,
        },
    }
