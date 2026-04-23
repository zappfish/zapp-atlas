"""PhenotypeObservationSet persistence + mapping."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from zapp_atlas.api.services.images import delete_image_row
from zapp_atlas.api.services.studies import (
    _obs_set_from_create,
    _phenotype_from_create,
)
from zapp_atlas.db.image_storage import Storage

from zebrafish_toxicology_atlas_schema.datamodel.pydanticmodel_v2 import (
    PhenotypeObservationSetCreate,
    PhenotypeObservationSetUpdate,
)

from zebrafish_toxicology_atlas_schema.datamodel.sqla import (  # type: ignore
    ExposureEvent,
    PhenotypeObservationSet,
)


def create_observation_for_exposure(
    session: Session,
    *,
    exposure_id: int,
    payload: PhenotypeObservationSetCreate,
) -> Optional[PhenotypeObservationSet]:
    exposure = session.get(ExposureEvent, exposure_id)
    if exposure is None:
        return None

    obs = _obs_set_from_create(session, payload)
    exposure.phenotype_observation.append(obs)
    session.add(exposure)
    session.commit()
    session.refresh(obs)
    return obs


def get_observation_by_id(
    session: Session, observation_id: int
) -> Optional[PhenotypeObservationSet]:
    return session.get(PhenotypeObservationSet, observation_id)


def patch_observation(
    session: Session,
    observation_id: int,
    patch: PhenotypeObservationSetUpdate,
) -> Optional[PhenotypeObservationSet]:
    obs = get_observation_by_id(session, observation_id)
    if obs is None:
        return None

    if patch.phenotype is not None:
        obs.phenotype = [_phenotype_from_create(session, p) for p in patch.phenotype]

    session.add(obs)
    session.commit()
    session.refresh(obs)
    return obs


def delete_observation_row(
    session: Session, obs: PhenotypeObservationSet, *, storage: Storage
) -> None:
    """Delete an observation set and all of its owned rows + image blobs."""
    for phenotype in list(obs.phenotype or []):
        session.delete(phenotype)
    for image in list(obs.image or []):
        delete_image_row(session, image, storage=storage)
    for ci in list(obs.control_image or []):
        session.delete(ci)
    session.delete(obs)


def delete_observation(
    session: Session, observation_id: int, *, storage: Storage
) -> bool:
    obs = get_observation_by_id(session, observation_id)
    if obs is None:
        return False
    delete_observation_row(session, obs, storage=storage)
    session.commit()
    return True
