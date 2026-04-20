"""Experiment endpoints.

Creation is scoped to a Study (no orphan experiments yet):

* POST /studies/{study_id}/experiments

Reading/listing is via a top-level experiments resource:

* GET /experiments
* GET /experiments/{experiment_id}
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.api.deps import get_session
from server.api.services.experiments import (
    create_experiment_for_study,
    delete_experiment,
    get_experiment_by_id,
    list_experiments,
    patch_experiment,
)
from server.storage import Storage, get_storage

from zebrafish_toxicology_atlas_schema.datamodel.pydanticmodel_v2 import (
    ExperimentCreate,
    ExperimentRead,
    ExperimentUpdate,
)


router = APIRouter(tags=["experiments"])


def _as_read(exp) -> ExperimentRead:
    return ExperimentRead.model_validate(exp, from_attributes=True)


@router.post(
    "/studies/{study_id}/experiments",
    response_model=ExperimentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_experiment_for_study_endpoint(
    study_id: int,
    payload: ExperimentCreate,
    session: Annotated[Session, Depends(get_session)],
) -> ExperimentRead:
    exp = create_experiment_for_study(session, study_id=study_id, payload=payload)
    if exp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
    return _as_read(exp)


@router.get("/experiments", response_model=list[ExperimentRead])
def list_experiments_endpoint(
    session: Annotated[Session, Depends(get_session)],
    limit: int = 50,
    offset: int = 0,
) -> list[ExperimentRead]:
    rows = list_experiments(session, limit=limit, offset=offset)
    return [_as_read(e) for e in rows]


@router.get("/experiments/{experiment_id}", response_model=ExperimentRead)
def get_experiment_endpoint(
    experiment_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> ExperimentRead:
    exp = get_experiment_by_id(session, experiment_id)
    if exp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found",
        )
    return _as_read(exp)


@router.patch("/experiments/{experiment_id}", response_model=ExperimentRead)
def patch_experiment_endpoint(
    experiment_id: int,
    patch: ExperimentUpdate,
    session: Annotated[Session, Depends(get_session)],
) -> ExperimentRead:
    exp = patch_experiment(session, experiment_id, patch)
    if exp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found",
        )
    return _as_read(exp)


@router.delete("/experiments/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experiment_endpoint(
    experiment_id: int,
    session: Annotated[Session, Depends(get_session)],
    storage: Annotated[Storage, Depends(get_storage)],
) -> None:
    if not delete_experiment(session, experiment_id, storage=storage):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found",
        )
