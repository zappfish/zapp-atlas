"""Experiment persistence + mapping.

We treat Experiment as the main unit of submission, with creation scoped to a
Study container.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from server.api.services.studies import _experiment_from_create

from zebrafish_toxicology_atlas_schema.datamodel.pydanticmodel_v2 import ExperimentCreate

from zebrafish_toxicology_atlas_schema.datamodel.sqla import (  # type: ignore
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
    try:
        return session.get(Experiment, experiment_id)
    except Exception:
        return session.query(Experiment).filter(Experiment.id == experiment_id).one_or_none()


def list_experiments(session: Session, *, limit: int = 50, offset: int = 0) -> list[Experiment]:
    q = session.query(Experiment).order_by(Experiment.id).offset(offset).limit(limit)
    return list(q)
