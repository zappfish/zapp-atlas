"""Experiment persistence + mapping.

We treat Experiment as the main unit of submission, with creation scoped to a
Study container.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from zapp_atlas.api.services.exposures import delete_exposure_row
from zapp_atlas.api.services.studies import _experiment_from_create, _fish_from_payload
from zapp_atlas.db.image_storage import Storage

from zapp_atlas.schema.pydantic_crud import (
    ExperimentCreate,
    ExperimentUpdate,
)

from zapp_atlas.schema.sqla import (  # type: ignore
    Experiment,
    Study,
)


def create_experiment_for_study(
    session: Session,
    *,
    study_id: int,
    payload: ExperimentCreate,
) -> Optional[Experiment]:
    """Create an Experiment belonging to an existing Study."""

    study = session.get(Study, study_id)
    if study is None:
        return None

    exp = _experiment_from_create(session, payload)
    # Associate with parent container
    study.experiment.append(exp)

    session.add(study)
    session.commit()
    session.refresh(exp)
    return exp


def get_experiment_by_id(session: Session, experiment_id: int) -> Optional[Experiment]:
    return session.get(Experiment, experiment_id)


def list_experiments(session: Session, *, limit: int = 50, offset: int = 0) -> list[Experiment]:
    q = session.query(Experiment).order_by(Experiment.id).offset(offset).limit(limit)
    return list(q)


def patch_experiment(
    session: Session, experiment_id: int, patch: ExperimentUpdate
) -> Optional[Experiment]:
    exp = get_experiment_by_id(session, experiment_id)
    if exp is None:
        return None

    if patch.standard_rearing_condition is not None:
        exp.standard_rearing_condition = patch.standard_rearing_condition
    if patch.rearing_condition_comment is not None:
        exp.rearing_condition_comment = patch.rearing_condition_comment
    if patch.fish is not None:
        exp.fish = _fish_from_payload(session, patch.fish)
    # control / exposure_event lists are intentionally not replaced on PATCH —
    # those have their own nested routes.

    session.add(exp)
    session.commit()
    session.refresh(exp)
    return exp


def delete_experiment_row(
    session: Session, exp: Experiment, *, storage: Storage
) -> None:
    for exposure in list(exp.exposure_event or []):
        delete_exposure_row(session, exposure, storage=storage)
    for control in list(exp.control or []):
        session.delete(control)
    session.delete(exp)


def delete_experiment(
    session: Session, experiment_id: int, *, storage: Storage
) -> bool:
    exp = get_experiment_by_id(session, experiment_id)
    if exp is None:
        return False
    delete_experiment_row(session, exp, storage=storage)
    session.commit()
    return True
