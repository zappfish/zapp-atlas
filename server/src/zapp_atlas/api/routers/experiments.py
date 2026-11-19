"""Experiment endpoints.

Created beneath a study, then read, replaced and deleted by its own id.
"""

from typing import Annotated

from fastapi import APIRouter, status

from zapp_atlas.api.authz import SignedIn
from zapp_atlas.api.deps import SessionDep, StorageDep
from zapp_atlas.api.resources import readable, writable
from zapp_atlas.api.services import levels
from zapp_atlas.schema.pydantic_crud import ExperimentInput, ExperimentRead
from zapp_atlas.schema.sqla import Experiment, Study

router = APIRouter(tags=["experiments"])

Readable = Annotated[Experiment, readable("Experiment")]
Writable = Annotated[Experiment, writable("Experiment")]
WritableParent = Annotated[Study, writable("Study")]


@router.post(
    "/studies/{study_id}/experiments",
    response_model=ExperimentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_experiment(
    parent: WritableParent, body: ExperimentInput, identity: SignedIn, session: SessionDep
) -> Experiment:
    return levels.create(session, "Experiment", body, parent=parent, by=identity)


@router.get("/experiments/{experiment_id}", response_model=ExperimentRead)
def read_experiment(experiment: Readable) -> Experiment:
    return experiment


@router.put("/experiments/{experiment_id}", response_model=ExperimentRead)
def replace_experiment(
    experiment: Writable, body: ExperimentInput, identity: SignedIn, session: SessionDep
) -> Experiment:
    return levels.replace(session, "Experiment", experiment, body, by=identity)


@router.delete("/experiments/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experiment(
    experiment: Writable, identity: SignedIn, session: SessionDep, storage: StorageDep
) -> None:
    levels.delete(session, "Experiment", experiment, storage, by=identity)
