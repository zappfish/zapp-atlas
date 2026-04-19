"""Exposure event endpoints.

* POST /experiments/{experiment_id}/exposures
* GET /exposures/{exposure_id}
* PATCH /exposures/{exposure_id}
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.api.deps import get_session
from server.api.read_models import ExposureEventReadWithLabels
from server.api.serializers import OrmView
from server.api.services.exposures import (
    create_exposure_for_experiment,
    delete_exposure,
    get_exposure_by_id,
    patch_exposure,
)
from server.storage import Storage, get_storage

from zebrafish_toxicology_atlas_schema.datamodel.pydanticmodel_v2 import (
    ExposureEventCreate,
    ExposureEventUpdate,
)


router = APIRouter(tags=["exposures"])
ExposureEventRead = ExposureEventReadWithLabels


def _as_read(ee) -> ExposureEventRead:
    return ExposureEventRead.model_validate(OrmView(ee), from_attributes=True)


@router.post(
    "/experiments/{experiment_id}/exposures",
    response_model=ExposureEventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_exposure_endpoint(
    experiment_id: int,
    payload: ExposureEventCreate,
    session: Annotated[Session, Depends(get_session)],
) -> ExposureEventRead:
    ee = create_exposure_for_experiment(
        session, experiment_id=experiment_id, payload=payload
    )
    if ee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found"
        )
    return _as_read(ee)


@router.get("/exposures/{exposure_id}", response_model=ExposureEventRead)
def get_exposure_endpoint(
    exposure_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> ExposureEventRead:
    ee = get_exposure_by_id(session, exposure_id)
    if ee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exposure not found"
        )
    return _as_read(ee)


@router.patch("/exposures/{exposure_id}", response_model=ExposureEventRead)
def patch_exposure_endpoint(
    exposure_id: int,
    patch: ExposureEventUpdate,
    session: Annotated[Session, Depends(get_session)],
) -> ExposureEventRead:
    ee = patch_exposure(session, exposure_id, patch)
    if ee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exposure not found"
        )
    return _as_read(ee)


@router.delete("/exposures/{exposure_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exposure_endpoint(
    exposure_id: int,
    session: Annotated[Session, Depends(get_session)],
    storage: Annotated[Storage, Depends(get_storage)],
) -> None:
    if not delete_exposure(session, exposure_id, storage=storage):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exposure not found"
        )
