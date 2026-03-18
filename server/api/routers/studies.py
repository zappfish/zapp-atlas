"""Study CRUD endpoints.

This router is intentionally thin: all persistence/mapping details are pushed
into `api.services.studies`.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.api.deps import get_session
from server.api.services.studies import (
    create_study,
    get_study_by_id,
    list_studies,
    patch_study,
)

# LinkML-generated Pydantic CRUD models
from zebrafish_toxicology_atlas_schema.datamodel.pydanticmodel_v2 import (
    StudyCreate,
    StudyRead,
    StudyUpdate,
)


router = APIRouter(prefix="/studies", tags=["studies"])


@router.post("", response_model=StudyRead, status_code=status.HTTP_201_CREATED)
def create_study_endpoint(
    payload: StudyCreate,
    session: Annotated[Session, Depends(get_session)],
) -> StudyRead:
    study = create_study(session, payload)
    # We return ORM instances; StudyRead is configured with from_attributes=True.
    return study  # type: ignore[return-value]


@router.get("/{study_id}", response_model=StudyRead)
def get_study_endpoint(
    study_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> StudyRead:
    study = get_study_by_id(session, study_id)
    if study is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
    return study  # type: ignore[return-value]


@router.get("", response_model=list[StudyRead])
def list_studies_endpoint(
    session: Annotated[Session, Depends(get_session)],
    limit: int = 50,
    offset: int = 0,
) -> list[StudyRead]:
    rows = list_studies(session, limit=limit, offset=offset)
    return rows  # type: ignore[return-value]


@router.patch("/{study_id}", response_model=StudyRead)
def patch_study_endpoint(
    study_id: int,
    patch: StudyUpdate,
    session: Annotated[Session, Depends(get_session)],
) -> StudyRead:
    study = patch_study(session, study_id, patch)
    if study is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
    return study  # type: ignore[return-value]
