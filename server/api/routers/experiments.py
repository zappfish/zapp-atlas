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
    get_experiment_by_id,
    list_experiments,
)

from zebrafish_toxicology_atlas_schema.datamodel.pydanticmodel_v2 import (
    ExperimentCreate,
    ExperimentRead,
)


router = APIRouter(tags=["experiments"])


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
    return exp  # type: ignore[return-value]


@router.get("/experiments", response_model=list[ExperimentRead])
def list_experiments_endpoint(
    session: Annotated[Session, Depends(get_session)],
    limit: int = 50,
    offset: int = 0,
) -> list[ExperimentRead]:
    rows = list_experiments(session, limit=limit, offset=offset)
    return rows  # type: ignore[return-value]


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
    return exp  # type: ignore[return-value]
