"""Research group + membership persistence."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from zapp_atlas.api.authz import orcid_curie
from zapp_atlas.api.persistence import commit_or_conflict
from zapp_atlas.auth.models import OrcidIdentity
from zapp_atlas.schema.pydantic_crud import ResearchGroupRoleEnum
from zapp_atlas.schema.sqla import ResearchGroup, ResearchGroupMember

LAST_ADMIN_DETAIL = (
    "A research group must keep at least one admin; "
    "promote another member before giving up this role"
)


def _is_last_admin(session: Session, membership: ResearchGroupMember) -> bool:
    """True if ``membership`` is the only admin its group has left."""
    if membership.role != ResearchGroupRoleEnum.admin.value:
        return False
    remaining = (
        session.query(ResearchGroupMember)
        .filter(
            ResearchGroupMember.research_group == membership.research_group,
            ResearchGroupMember.role == ResearchGroupRoleEnum.admin.value,
        )
        .count()
    )
    return remaining <= 1


def _reject_if_last_admin(session: Session, membership: ResearchGroupMember) -> None:
    """Refuse a change that would leave the group with nobody who can manage it.

    Shared by the two paths that can strip an admin role — demotion and
    removal — so the invariant holds however the role goes away.
    """
    if _is_last_admin(session, membership):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=LAST_ADMIN_DETAIL)


def create_group(session: Session, name: str, creator: OrcidIdentity) -> ResearchGroup:
    """Create a group and enroll the creator as its first admin."""
    group = ResearchGroup(name=name)
    session.add(group)
    session.flush()  # assign group.id before the membership row references it
    session.add(
        ResearchGroupMember(
            research_group=group.id,
            member=orcid_curie(creator.orcid_id),
            role=ResearchGroupRoleEnum.admin.value,
        )
    )
    commit_or_conflict(session, "Could not create research group")
    session.refresh(group)
    return group


def list_groups_for(session: Session, identity: OrcidIdentity) -> list[ResearchGroup]:
    return (
        session.query(ResearchGroup)
        .join(
            ResearchGroupMember,
            ResearchGroupMember.research_group == ResearchGroup.id,
        )
        .filter(ResearchGroupMember.member == orcid_curie(identity.orcid_id))
        .order_by(ResearchGroup.id)
        .all()
    )


def list_members(session: Session, group_id: int) -> list[ResearchGroupMember]:
    return (
        session.query(ResearchGroupMember)
        .filter(ResearchGroupMember.research_group == group_id)
        .order_by(ResearchGroupMember.id)
        .all()
    )


def add_member(session: Session, group_id: int, member: str, role: str) -> ResearchGroupMember:
    membership = ResearchGroupMember(research_group=group_id, member=orcid_curie(member), role=role)
    session.add(membership)
    commit_or_conflict(session, "That ORCID is already a member of this group")
    session.refresh(membership)
    return membership


def get_membership(session: Session, group_id: int, member_id: int) -> ResearchGroupMember | None:
    """Load a membership *scoped to its group*, so ids don't leak across groups."""
    return (
        session.query(ResearchGroupMember)
        .filter(
            ResearchGroupMember.id == member_id,
            ResearchGroupMember.research_group == group_id,
        )
        .one_or_none()
    )


def update_member_role(
    session: Session, group_id: int, member_id: int, role: str
) -> ResearchGroupMember | None:
    """Change a member's role. ``None`` if no such membership under this group.

    ``role`` is the only mutable field: ``member`` and ``research_group`` are
    identity, and changing either describes a different membership.
    """
    membership = get_membership(session, group_id, member_id)
    if membership is None:
        return None
    if role != ResearchGroupRoleEnum.admin.value:
        _reject_if_last_admin(session, membership)
    membership.role = role
    commit_or_conflict(session, "Could not update this membership")
    session.refresh(membership)
    return membership


def remove_member(session: Session, group_id: int, member_id: int) -> bool:
    membership = get_membership(session, group_id, member_id)
    if membership is None:
        return False
    _reject_if_last_admin(session, membership)
    session.delete(membership)
    session.commit()
    return True
