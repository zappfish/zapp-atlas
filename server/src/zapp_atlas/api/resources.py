"""Loading the study-tree resource a path names, and deciding who may touch it.

A route asks for the row it works on as a parameter::

    def replace(experiment: Annotated[Experiment, writable("Experiment")], ...)

and gets it already loaded. Every level is authorized against the study that
contains it:

* ``readable`` -- anyone, once the study is published. While it is a draft only
  members of its research group may see it, and everyone else gets the same
  404 as for a row that does not exist.
* ``writable`` -- members of the study's research group. A signed-out caller
  gets a 401, and one from another group a 403.
"""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Path, params, status
from sqlalchemy.orm import Session

from zapp_atlas.api.authz import SignedIn, is_member, require_membership
from zapp_atlas.api.deps import SessionDep
from zapp_atlas.api.layout import Level, layout
from zapp_atlas.auth.deps import CurrentIdentity
from zapp_atlas.schema import sqla
from zapp_atlas.schema.pydantic_crud import StudyStatusEnum
from zapp_atlas.schema.sqla import Base, Study

# What each level's id is called in a path.
PATH_PARAMETERS = {
    "Study": "study_id",
    "Experiment": "experiment_id",
    "ExposureEvent": "exposure_id",
    "PhenotypeObservationSet": "observation_id",
    "Image": "image_id",
}


def study_of(session: Session, level: Level, row: Base) -> Study:
    """The study a row sits in, however many levels down it is."""
    while level.parent is not None:
        # ``gen-sqla`` names a child's foreign key after its parent's class.
        parent_id = getattr(row, f"{level.parent.name}_id")
        row = session.get_one(getattr(sqla, level.parent.name), parent_id)
        level = level.parent
    return row


def readable(level_name: str) -> params.Depends:
    """A dependency giving the row the path names, if the caller may see it."""
    level = layout().levels[level_name]
    find = _finder(level_name)

    def load(identity: CurrentIdentity, session: SessionDep, row_id: _row_id(level_name)) -> Base:
        row = find(session, row_id)
        study = study_of(session, level, row)
        if study.status != StudyStatusEnum.published.value and not is_member(
            session, study.research_group, identity
        ):
            raise _not_found(level_name)
        return row

    return Depends(load)


def writable(level_name: str) -> params.Depends:
    """A dependency giving the row the path names, if the caller may change it."""
    level = layout().levels[level_name]
    find = _finder(level_name)

    def load(identity: SignedIn, session: SessionDep, row_id: _row_id(level_name)) -> Base:
        row = find(session, row_id)
        study = study_of(session, level, row)
        if not is_member(session, study.research_group, identity):
            if study.status != StudyStatusEnum.published.value:
                raise _not_found(level_name)
            require_membership(session, study.research_group, identity)
        return row

    return Depends(load)


def _row_id(level_name: str) -> object:
    """The path parameter holding a level's id, whatever that level calls it."""
    return Annotated[int, Path(alias=PATH_PARAMETERS[level_name])]


def _not_found(level_name: str) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, f"{level_name} not found")


def _finder(level_name: str) -> Callable[[Session, int], Base]:
    model = getattr(sqla, level_name)

    def find(session: Session, row_id: int) -> Base:
        row = session.get(model, row_id)
        if row is None:
            raise _not_found(level_name)
        return row

    return find
