"""Local extensions of the schema's Read models.

The LinkML-generated ``ExposureEventRead`` exposes ``route`` and
``exposure_type`` as bare CURIE strings; we also want the human-readable
label alongside, pulled from the ``ExposureRoute`` / ``ExposureType`` rows
we maintain locally. Re-declaring just the exposure node would mean the
parent chain (ExperimentRead → StudyRead) keeps pointing at the base class
and strips the new fields, so we re-parent the whole chain here.

``OrmView`` (see ``serializers.py``) materializes the extra attributes;
this module just declares the shape Pydantic validates against.
"""

from __future__ import annotations

from typing import Optional

from zebrafish_toxicology_atlas_schema.datamodel.pydanticmodel_v2 import (
    ExperimentRead,
    ExposureEventRead,
    StudyRead,
)


class ExposureEventReadWithLabels(ExposureEventRead):
    route_label: Optional[str] = None
    exposure_type_label: Optional[str] = None


class ExperimentReadWithLabels(ExperimentRead):
    exposure_event: Optional[list[ExposureEventReadWithLabels]] = None


class StudyReadWithLabels(StudyRead):
    experiment: Optional[list[ExperimentReadWithLabels]] = None
