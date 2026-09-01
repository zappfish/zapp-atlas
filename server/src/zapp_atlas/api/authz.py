"""Research-group authorization for the API.

Cabinet and fish-tank resources are private to a research group, so their
endpoints depend on membership rather than merely being signed in. These
dependencies resolve the signed-in ORCID identity to a membership row and
enforce the member/admin split:

- ``require_current_identity`` — signed in, or 401.
- ``require_group_member``   — a member of the group in the path, or 403.
- ``require_group_admin``    — an *admin* of that group, or 403.

The signed-in identity stores a bare ORCID (``0000-...``) while the schema
stores ``member`` as a CURIE (``ORCID:0000-...``); ``orcid_curie`` bridges
that seam so the membership lookup compares like with like.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from zapp_atlas.api.deps import get_session
from zapp_atlas.auth.deps import get_current_identity
from zapp_atlas.auth.models import OrcidIdentity
from zapp_atlas.schema.pydantic_crud import ResearchGroupRoleEnum
from zapp_atlas.schema.sqla import ResearchGroup, ResearchGroupMember

ORCID_CURIE_PREFIX = "ORCID:"


def orcid_curie(orcid_id: str) -> str:
    """Normalize a bare ORCID to the ``ORCID:`` CURIE the schema stores."""
    if orcid_id.startswith(ORCID_CURIE_PREFIX):
        return orcid_id
    return f"{ORCID_CURIE_PREFIX}{orcid_id}"


@dataclass(frozen=True)
class GroupContext:
    """The signed-in caller together with their membership in a group."""

    identity: OrcidIdentity
    membership: ResearchGroupMember

    @property
    def is_admin(self) -> bool:
        return self.membership.role == ResearchGroupRoleEnum.admin.value


def require_current_identity(
    identity: Annotated[OrcidIdentity | None, Depends(get_current_identity)],
) -> OrcidIdentity:
    if identity is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return identity


def _load_group(session: Session, group_id: int) -> ResearchGroup:
    group = session.get(ResearchGroup, group_id)
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research group not found",
        )
    return group


def _find_membership(
    session: Session, group_id: int, identity: OrcidIdentity
) -> ResearchGroupMember | None:
    return (
        session.query(ResearchGroupMember)
        .filter(
            ResearchGroupMember.research_group == group_id,
            ResearchGroupMember.member == orcid_curie(identity.orcid_id),
        )
        .one_or_none()
    )


def require_group_member(
    group_id: int,
    session: Annotated[Session, Depends(get_session)],
    identity: Annotated[OrcidIdentity, Depends(require_current_identity)],
) -> GroupContext:
    """Caller must be a member of ``group_id``.

    A non-member gets the *same* 404 as a missing group: group membership is
    private, so we don't reveal which ids exist to people outside the group.
    """
    _load_group(session, group_id)
    membership = _find_membership(session, group_id, identity)
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research group not found",
        )
    return GroupContext(identity=identity, membership=membership)


def require_group_admin(
    context: Annotated[GroupContext, Depends(require_group_member)],
) -> GroupContext:
    """Caller must be an *admin* of the group (gates membership changes)."""
    if not context.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required for this action",
        )
    return context


GroupMember = Annotated[GroupContext, Depends(require_group_member)]
GroupAdmin = Annotated[GroupContext, Depends(require_group_admin)]
