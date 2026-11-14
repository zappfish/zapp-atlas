"""Study endpoints.

A study's body carries the study's own fields. Its experiments are resources of
their own, created beneath it and saved separately; reading a study returns them
all the same, so one request loads the whole tree.
"""

from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_, select

from zapp_atlas.api.authz import SignedIn, groups_of, require_membership
from zapp_atlas.api.deps import SessionDep, StorageDep
from zapp_atlas.api.models import Revision, RevisionSummary
from zapp_atlas.api.resources import readable, writable
from zapp_atlas.api.services import levels
from zapp_atlas.auth.deps import CurrentIdentity
from zapp_atlas.db.revisions import StudyRevision
from zapp_atlas.schema.pydantic_crud import StudyInput, StudyRead, StudyStatusEnum, StudySummary
from zapp_atlas.schema.sqla import Study

router = APIRouter(prefix="/studies", tags=["studies"])

Readable = Annotated[Study, readable("Study")]
Writable = Annotated[Study, writable("Study")]


@router.get("", response_model=list[StudySummary])
def list_studies(
    session: SessionDep,
    identity: CurrentIdentity,
    research_group: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Study]:
    """Published studies, and the drafts of the caller's own research groups."""
    visible = or_(
        Study.status == StudyStatusEnum.published.value,
        Study.research_group.in_(groups_of(session, identity)),
    )
    query = select(Study).where(visible).order_by(Study.id).offset(offset).limit(limit)
    if research_group is not None:
        query = query.where(Study.research_group == research_group)
    return list(session.scalars(query))


@router.post("", response_model=StudyRead, status_code=status.HTTP_201_CREATED)
def create_study(body: StudyInput, identity: SignedIn, session: SessionDep) -> Study:
    require_membership(session, body.research_group, identity)
    return levels.create(session, "Study", body, parent=None, by=identity)


@router.get("/{study_id}", response_model=StudyRead)
def read_study(study: Readable) -> Study:
    return study


@router.put("/{study_id}", response_model=StudyRead)
def replace_study(
    study: Writable, body: StudyInput, identity: SignedIn, session: SessionDep
) -> Study:
    # Moving a study to another group takes membership of both.
    require_membership(session, body.research_group, identity)
    return levels.replace(session, "Study", study, body, by=identity)


@router.delete("/{study_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_study(
    study: Writable, identity: SignedIn, session: SessionDep, storage: StorageDep
) -> None:
    levels.delete(session, "Study", study, storage, by=identity)


@router.get("/{study_id}/revisions", response_model=list[RevisionSummary])
def list_revisions(study: Readable, session: SessionDep) -> list[StudyRevision]:
    """Every save made to a study or anything beneath it, oldest first."""
    return list(
        session.scalars(
            select(StudyRevision)
            .where(StudyRevision.study_id == study.id)
            .order_by(StudyRevision.version)
        )
    )


@router.get("/{study_id}/revisions/{version}", response_model=Revision)
def read_revision(study: Readable, version: int, session: SessionDep) -> StudyRevision:
    revision = session.scalar(
        select(StudyRevision).where(
            StudyRevision.study_id == study.id, StudyRevision.version == version
        )
    )
    if revision is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Revision not found")
    return revision
