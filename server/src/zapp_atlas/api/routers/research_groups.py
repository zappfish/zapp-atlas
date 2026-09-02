"""Research group + membership endpoints.

A minimal surface: create a group (creator becomes admin), list the groups you
belong to, and manage membership. Membership changes require the admin role;
everything else requires being a member. A group must always retain at least
one admin, so the last one can be neither demoted nor removed. The rest of
membership management (invites, leaving a group, ownership transfer) is
tracked separately (#104).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from zapp_atlas.api.authz import (
    GroupAdmin,
    GroupMember,
    require_current_identity,
)
from zapp_atlas.api.deps import get_session
from zapp_atlas.api.dto import MemberIn, MemberOut, MemberPatch
from zapp_atlas.api.services.research_groups import (
    add_member,
    create_group,
    list_groups_for,
    list_members,
    remove_member,
    update_member_role,
)
from zapp_atlas.auth.models import OrcidIdentity
from zapp_atlas.schema.pydantic_crud import ResearchGroupCreate, ResearchGroupRead
from zapp_atlas.schema.sqla import ResearchGroup

router = APIRouter(prefix="/research-groups", tags=["research-groups"])

SessionDep = Annotated[Session, Depends(get_session)]
CurrentIdentity = Annotated[OrcidIdentity, Depends(require_current_identity)]


def _group_read(group: ResearchGroup) -> ResearchGroupRead:
    return ResearchGroupRead.model_validate(group, from_attributes=True)


@router.post("", response_model=ResearchGroupRead, status_code=status.HTTP_201_CREATED)
def create_group_endpoint(
    payload: ResearchGroupCreate,
    session: SessionDep,
    identity: CurrentIdentity,
) -> ResearchGroupRead:
    return _group_read(create_group(session, payload.name, identity))


@router.get("", response_model=list[ResearchGroupRead])
def list_my_groups_endpoint(
    session: SessionDep,
    identity: CurrentIdentity,
) -> list[ResearchGroupRead]:
    return [_group_read(g) for g in list_groups_for(session, identity)]


@router.get("/{group_id}", response_model=ResearchGroupRead)
def get_group_endpoint(
    group_id: int,
    session: SessionDep,
    _: GroupMember,
) -> ResearchGroupRead:
    # GroupMember has already loaded the group and enforced access.
    return _group_read(session.get(ResearchGroup, group_id))


@router.get("/{group_id}/members", response_model=list[MemberOut])
def list_members_endpoint(
    group_id: int,
    session: SessionDep,
    _: GroupMember,
) -> list[MemberOut]:
    return [MemberOut.model_validate(m) for m in list_members(session, group_id)]


@router.post(
    "/{group_id}/members",
    response_model=MemberOut,
    status_code=status.HTTP_201_CREATED,
)
def add_member_endpoint(
    group_id: int,
    payload: MemberIn,
    session: SessionDep,
    _: GroupAdmin,
) -> MemberOut:
    membership = add_member(session, group_id, payload.member, payload.role.value)
    return MemberOut.model_validate(membership)


@router.patch("/{group_id}/members/{member_id}", response_model=MemberOut)
def update_member_endpoint(
    group_id: int,
    member_id: int,
    payload: MemberPatch,
    session: SessionDep,
    _: GroupAdmin,
) -> MemberOut:
    membership = update_member_role(session, group_id, member_id, payload.role.value)
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")
    return MemberOut.model_validate(membership)


@router.delete(
    "/{group_id}/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_member_endpoint(
    group_id: int,
    member_id: int,
    session: SessionDep,
    _: GroupAdmin,
) -> None:
    if not remove_member(session, group_id, member_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")
