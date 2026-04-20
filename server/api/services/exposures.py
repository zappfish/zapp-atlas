"""Exposure event persistence + mapping."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from server.api.services.observations import delete_observation_row
from server.api.services.studies import (
    _exposure_event_from_create,
    _quantity_value_from_payload,
    _regimen_from_create,
    _resolve_ontology_term,
    _stressor_from_create,
    _vehicle_from_payload,
)
from server.storage import Storage

from zebrafish_toxicology_atlas_schema.datamodel.pydanticmodel_v2 import (
    ExposureEventCreate,
    ExposureEventUpdate,
)

from zebrafish_toxicology_atlas_schema.datamodel.sqla import (  # type: ignore
    Experiment,
    ExposureEvent,
    VehicleOfTransmission,
)


def create_exposure_for_experiment(
    session: Session,
    *,
    experiment_id: int,
    payload: ExposureEventCreate,
) -> Optional[ExposureEvent]:
    experiment = session.get(Experiment, experiment_id)
    if experiment is None:
        return None

    ee = _exposure_event_from_create(session, payload)
    experiment.exposure_event.append(ee)
    session.add(experiment)
    session.commit()
    session.refresh(ee)
    return ee


def get_exposure_by_id(session: Session, exposure_id: int) -> Optional[ExposureEvent]:
    return session.get(ExposureEvent, exposure_id)


def patch_exposure(
    session: Session, exposure_id: int, patch: ExposureEventUpdate
) -> Optional[ExposureEvent]:
    ee = get_exposure_by_id(session, exposure_id)
    if ee is None:
        return None

    scalar_fields = (
        "exposure_start_stage",
        "exposure_end_stage",
        "comment",
        "additional_exposure_condition",
    )
    for field in scalar_fields:
        value = getattr(patch, field, None)
        if value is not None:
            setattr(ee, field, value)

    # Ontology-validated relationships.
    if patch.route is not None:
        ee.route = _resolve_ontology_term(session, "route", patch.route)
    if patch.exposure_type is not None:
        ee.exposure_type = _resolve_ontology_term(
            session, "exposure_type", patch.exposure_type
        )

    if patch.vehicle is not None:
        ee.vehicle = [_vehicle_from_payload(v) for v in patch.vehicle]

    if patch.regimen is not None:
        ee.regimen = _regimen_from_create(session, patch.regimen)

    if patch.stressor is not None:
        ee.stressor = [_stressor_from_create(session, s) for s in patch.stressor]

    session.add(ee)
    session.commit()
    session.refresh(ee)
    return ee


def delete_exposure_row(
    session: Session, ee: ExposureEvent, *, storage: Storage
) -> None:
    for obs in list(ee.phenotype_observation or []):
        delete_observation_row(session, obs, storage=storage)
    for stressor in list(ee.stressor or []):
        session.delete(stressor)
    session.query(VehicleOfTransmission).filter_by(
        ExposureEvent_id=ee.id
    ).delete(synchronize_session="fetch")
    if ee.regimen is not None:
        session.delete(ee.regimen)
    session.delete(ee)


def delete_exposure(
    session: Session, exposure_id: int, *, storage: Storage
) -> bool:
    ee = get_exposure_by_id(session, exposure_id)
    if ee is None:
        return False
    delete_exposure_row(session, ee, storage=storage)
    session.commit()
    return True
