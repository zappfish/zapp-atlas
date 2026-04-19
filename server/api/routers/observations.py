"""PhenotypeObservationSet endpoints.

* POST /exposures/{exposure_id}/observations
* GET /observations/{observation_id}
* PATCH /observations/{observation_id}
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.api.deps import get_session
from server.api.services.observations import (
    create_observation_for_exposure,
    delete_observation,
    get_observation_by_id,
    patch_observation,
)
from server.storage import Storage, get_storage

from zebrafish_toxicology_atlas_schema.datamodel.pydanticmodel_v2 import (
    PhenotypeObservationSetCreate,
    PhenotypeObservationSetRead,
    PhenotypeObservationSetUpdate,
)


router = APIRouter(tags=["observations"])


@router.post(
    "/exposures/{exposure_id}/observations",
    response_model=PhenotypeObservationSetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_observation_endpoint(
    exposure_id: int,
    payload: PhenotypeObservationSetCreate,
    session: Annotated[Session, Depends(get_session)],
) -> PhenotypeObservationSetRead:
    obs = create_observation_for_exposure(
        session, exposure_id=exposure_id, payload=payload
    )
    if obs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exposure not found"
        )
    return obs  # type: ignore[return-value]


@router.get("/observations/{observation_id}", response_model=PhenotypeObservationSetRead)
def get_observation_endpoint(
    observation_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> PhenotypeObservationSetRead:
    obs = get_observation_by_id(session, observation_id)
    if obs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found"
        )
    return obs  # type: ignore[return-value]


@router.patch(
    "/observations/{observation_id}", response_model=PhenotypeObservationSetRead
)
def patch_observation_endpoint(
    observation_id: int,
    patch: PhenotypeObservationSetUpdate,
    session: Annotated[Session, Depends(get_session)],
) -> PhenotypeObservationSetRead:
    obs = patch_observation(session, observation_id, patch)
    if obs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found"
        )
    return obs  # type: ignore[return-value]


@router.delete(
    "/observations/{observation_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_observation_endpoint(
    observation_id: int,
    session: Annotated[Session, Depends(get_session)],
    storage: Annotated[Storage, Depends(get_storage)],
) -> None:
    if not delete_observation(session, observation_id, storage=storage):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found"
        )
