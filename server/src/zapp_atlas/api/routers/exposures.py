"""Exposure event endpoints.

Created beneath an experiment, then read, replaced and deleted by its own id.
"""

from typing import Annotated

from fastapi import APIRouter, status

from zapp_atlas.api.authz import SignedIn
from zapp_atlas.api.deps import SessionDep, StorageDep
from zapp_atlas.api.resources import readable, writable
from zapp_atlas.api.services import levels
from zapp_atlas.schema.pydantic_crud import ExposureEventInput, ExposureEventRead
from zapp_atlas.schema.sqla import Experiment, ExposureEvent

router = APIRouter(tags=["exposures"])

Readable = Annotated[ExposureEvent, readable("ExposureEvent")]
Writable = Annotated[ExposureEvent, writable("ExposureEvent")]
WritableParent = Annotated[Experiment, writable("Experiment")]


@router.post(
    "/experiments/{experiment_id}/exposures",
    response_model=ExposureEventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_exposure(
    parent: WritableParent, body: ExposureEventInput, identity: SignedIn, session: SessionDep
) -> ExposureEvent:
    return levels.create(session, "ExposureEvent", body, parent=parent, by=identity)


@router.get("/exposures/{exposure_id}", response_model=ExposureEventRead)
def read_exposure(exposure: Readable) -> ExposureEvent:
    return exposure


@router.put("/exposures/{exposure_id}", response_model=ExposureEventRead)
def replace_exposure(
    exposure: Writable, body: ExposureEventInput, identity: SignedIn, session: SessionDep
) -> ExposureEvent:
    return levels.replace(session, "ExposureEvent", exposure, body, by=identity)


@router.delete("/exposures/{exposure_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exposure(
    exposure: Writable, identity: SignedIn, session: SessionDep, storage: StorageDep
) -> None:
    levels.delete(session, "ExposureEvent", exposure, storage, by=identity)
