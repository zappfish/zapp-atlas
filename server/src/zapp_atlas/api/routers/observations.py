"""Observation endpoints.

Created beneath an exposure event, then read, replaced and deleted by its own id.
"""

from typing import Annotated

from fastapi import APIRouter, status

from zapp_atlas.api.authz import SignedIn
from zapp_atlas.api.deps import SessionDep, StorageDep
from zapp_atlas.api.resources import readable, writable
from zapp_atlas.api.services import levels
from zapp_atlas.schema.pydantic_crud import (
    PhenotypeObservationSetInput,
    PhenotypeObservationSetRead,
)
from zapp_atlas.schema.sqla import ExposureEvent, PhenotypeObservationSet

router = APIRouter(tags=["observations"])

Readable = Annotated[PhenotypeObservationSet, readable("PhenotypeObservationSet")]
Writable = Annotated[PhenotypeObservationSet, writable("PhenotypeObservationSet")]
WritableParent = Annotated[ExposureEvent, writable("ExposureEvent")]


@router.post(
    "/exposures/{exposure_id}/observations",
    response_model=PhenotypeObservationSetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_observation(
    parent: WritableParent,
    body: PhenotypeObservationSetInput,
    identity: SignedIn,
    session: SessionDep,
) -> PhenotypeObservationSet:
    return levels.create(session, "PhenotypeObservationSet", body, parent=parent, by=identity)


@router.get("/observations/{observation_id}", response_model=PhenotypeObservationSetRead)
def read_observation(observation: Readable) -> PhenotypeObservationSet:
    return observation


@router.put("/observations/{observation_id}", response_model=PhenotypeObservationSetRead)
def replace_observation(
    observation: Writable,
    body: PhenotypeObservationSetInput,
    identity: SignedIn,
    session: SessionDep,
) -> PhenotypeObservationSet:
    return levels.replace(session, "PhenotypeObservationSet", observation, body, by=identity)


@router.delete("/observations/{observation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_observation(
    observation: Writable, identity: SignedIn, session: SessionDep, storage: StorageDep
) -> None:
    levels.delete(session, "PhenotypeObservationSet", observation, storage, by=identity)
