"""Loading the study-tree resource a path names, and deciding who may touch it.

A route asks for the row it works on as a parameter::

    def replace(experiment: Annotated[Experiment, writable("Experiment")], ...)

and gets it already loaded, with a 404 for a row that does not exist and, for
``writable``, a 401 or 403 for a caller who may not change it. Every level is
authorized against the study that contains it.
"""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Path, params, status
from sqlalchemy.orm import Session

from zapp_atlas.api.authz import SignedIn, require_membership
from zapp_atlas.api.deps import SessionDep
from zapp_atlas.api.layout import Level, layout
from zapp_atlas.schema import sqla
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
    """A dependency giving the row of ``level_name`` that the path names."""
    return Depends(_loader(level_name))


def writable(level_name: str) -> params.Depends:
    """As ``readable``, but only for a member of the group that owns the study."""
    level = layout().levels[level_name]
    load = _loader(level_name)

    def load_for_writing(
        identity: SignedIn, session: SessionDep, row: Annotated[Base, Depends(load)]
    ) -> Base:
        require_membership(session, study_of(session, level, row).research_group, identity)
        return row

    return Depends(load_for_writing)


def _loader(level_name: str) -> Callable[..., Base]:
    model = getattr(sqla, level_name)
    parameter = PATH_PARAMETERS[level_name]

    def load(session: SessionDep, row_id: Annotated[int, Path(alias=parameter)]) -> Base:
        row = session.get(model, row_id)
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"{level_name} not found")
        return row

    return load
