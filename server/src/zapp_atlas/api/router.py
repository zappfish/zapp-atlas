from fastapi import APIRouter

from zapp_atlas.api.models import (
    StudyPayload,
    ExperimentPayload,
    ExposureEventPayload,
    ObservationPayload,
)

router = APIRouter()


@router.get("/health")
def health():
    return {"ok": True}


# -------------------------
# Study
# -------------------------

@router.post("/studies")
def create_study(payload: StudyPayload):
    return {
        "action": "create_study",
        "payload": payload.model_dump(),
    }


@router.put("/studies/{study_id}")
def update_study(study_id: int, payload: StudyPayload):
    return {
        "action": "update_study",
        "study_id": study_id,
        "payload": payload.model_dump(),
    }


# -------------------------
# Experiment
# -------------------------

@router.post("/studies/{study_id}/experiments")
def create_experiment(study_id: int, payload: ExperimentPayload):
    return {
        "action": "create_experiment",
        "study_id": study_id,
        "payload": payload.model_dump(),
    }


@router.put("/experiments/{experiment_id}")
def update_experiment(
    experiment_id: int,
    payload: ExperimentPayload,
):
    return {
        "action": "update_experiment",
        "experiment_id": experiment_id,
        "payload": payload.model_dump(),
    }


# -------------------------
# Exposure Event
# -------------------------

@router.post("/experiments/{experiment_id}/exposures")
def create_exposure_event(
    experiment_id: int,
    payload: ExposureEventPayload,
):
    return {
        "action": "create_exposure_event",
        "experiment_id": experiment_id,
        "payload": payload.model_dump(),
    }


@router.put("/exposures/{exposure_event_id}")
def update_exposure_event(
    exposure_event_id: int,
    payload: ExposureEventPayload,
):
    return {
        "action": "update_exposure_event",
        "exposure_event_id": exposure_event_id,
        "payload": payload.model_dump(),
    }


# -------------------------
# Observation
# -------------------------

@router.post("/exposures/{exposure_event_id}/observations")
def create_observation(
    exposure_event_id: int,
    payload: ObservationPayload,
):
    return {
        "action": "create_observation",
        "exposure_event_id": exposure_event_id,
        "payload": payload.model_dump(),
    }


@router.put("/observations/{observation_id}")
def update_observation(
    observation_id: int,
    payload: ObservationPayload,
):
    return {
        "action": "update_observation",
        "observation_id": observation_id,
        "payload": payload.model_dump(),
    }
