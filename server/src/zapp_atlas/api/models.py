from typing import Optional

from pydantic import BaseModel, ConfigDict

import zapp_atlas.schema.pydantic as schema


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


# -------------------------
# Study (provenance container)
# -------------------------

class StudyPayload(APIModel):
    publication: Optional[str] = None
    annotator: Optional[list[str]] = None
    lab: Optional[str] = None


# -------------------------
# Experiment (fish + rearing context)
# -------------------------

class ExperimentPayload(APIModel):
    standard_rearing_condition: Optional[bool] = None
    rearing_condition_comment: Optional[str] = None
    fish: Optional[schema.Fish] = None


# -------------------------
# Exposure Event (chemical + exposure context)
# -------------------------

class ExposureEventPayload(APIModel):
    stressor: Optional[list[schema.StressorChemical]] = None
    vehicle: Optional[list[schema.VehicleEnumeration]] = None
    route: Optional[schema.ExposureRouteEnum] = None
    regimen: Optional[schema.Regimen] = None

    exposure_start_stage: Optional[str] = None
    exposure_end_stage: Optional[str] = None
    exposure_type: Optional[schema.ExposureTypeEnum] = None
    additional_exposure_condition: Optional[str] = None
    comment: Optional[str] = None


# -------------------------
# Observation Set (main unit of work)
# -------------------------

class ObservationPhenotype(APIModel):
    stage: Optional[str] = None
    prevalence: Optional[schema.QuantityValue] = None
    severity: Optional[schema.SeverityEnum] = None

    # flattened ontology reference for API boundary
    phenotype_term_uri: Optional[str] = None
    phenotype_term_label: Optional[str] = None


class ObservationPayload(APIModel):
    phenotype: Optional[list[ObservationPhenotype]] = None
    image: Optional[list[schema.Image]] = None
    control_image: Optional[list[schema.ControlImage]] = None
