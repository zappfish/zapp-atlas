"""Research group + membership persistence."""

from __future__ import annotations

from collections.abc import Callable

from sqlalchemy.orm import Session

from zapp_atlas.api.authz import ORCID_CURIE_PREFIX, orcid_curie
from zapp_atlas.api.persistence import commit_or_conflict
from zapp_atlas.auth.models import OrcidIdentity
from zapp_atlas.auth.services import ensure_orcid_identity
from zapp_atlas.schema.pydantic_crud import ResearchGroupRoleEnum
from zapp_atlas.schema.sqla import ResearchGroup, ResearchGroupMember


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


def list_members(session: Session, group_id: int) -> list[tuple[ResearchGroupMember, str | None]]:
    """Memberships with each member's display name, where one is known.

    Membership stores an ``ORCID:`` CURIE while ``OrcidIdentity`` stores the
    bare ORCID, so the outer join concatenates the prefix back on.
    """
    return (
        session.query(ResearchGroupMember, OrcidIdentity.name)
        .outerjoin(
            OrcidIdentity,
            ResearchGroupMember.member == ORCID_CURIE_PREFIX + OrcidIdentity.orcid_id,
        )
        .filter(ResearchGroupMember.research_group == group_id)
        .order_by(ResearchGroupMember.id)
        .all()
    )


def add_member(
    session: Session,
    group_id: int,
    member: str,
    role: str,
    name_lookup: Callable[[str], str | None] | None = None,
) -> tuple[ResearchGroupMember, str | None]:
    """Add a member and make sure an ``OrcidIdentity`` exists for them.

    The added person may never have logged in, so ``name_lookup`` (the ORCID
    public API in production) supplies a display name for a newly created
    identity. An identity that already exists keeps its name — that one came
    from the person's own login.
    """
    curie = orcid_curie(member)
    orcid_id = curie.removeprefix(ORCID_CURIE_PREFIX)
    # Before the membership joins the session: ensure's SELECT would autoflush
    # a duplicate membership and raise outside commit_or_conflict's 409.
    identity = ensure_orcid_identity(session, orcid_id, name_lookup=name_lookup)

    membership = ResearchGroupMember(research_group=group_id, member=curie, role=role)
    session.add(membership)
    commit_or_conflict(session, "That ORCID is already a member of this group")
    session.refresh(membership)
    return membership, identity.name


def remove_member(session: Session, group_id: int, member_id: int) -> bool:
    membership = (
        session.query(ResearchGroupMember)
        .filter(
            ResearchGroupMember.id == member_id,
            ResearchGroupMember.research_group == group_id,
        )
        .one_or_none()
    )
    if membership is None:
        return False
    session.delete(membership)
    session.commit()
    return True
