"""Study persistence + mapping.

The intent here is to keep all of the "how do I convert StudyCreate to ORM"
logic in one place, so the router stays clean.

This code assumes LinkML-generated SQLAlchemy ORM classes are available at:
`zebrafish_toxicology_atlas_schema.datamodel.sqla`.
"""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

from zebrafish_toxicology_atlas_schema.datamodel.pydanticmodel_v2 import (
    ControlCreate,
    ExposureEventCreate,
    ExperimentCreate,
    PhenotypeCreate,
    PhenotypeObservationSetCreate,
    RegimenCreate,
    StressorChemicalCreate,
    StudyCreate,
    StudyUpdate,
)

# LinkML-generated SQLAlchemy models (present on another branch per user).
from zebrafish_toxicology_atlas_schema.datamodel.sqla import (  # type: ignore
    ChemicalEntity,
    Control,
    ExposureEvent,
    ExposureRoute,
    ExposureType,
    Experiment,
    Fish,
    Phenotype,
    PhenotypeObservationSet,
    PhenotypeTerm,
    QuantityValue,
    Regimen,
    StressorChemical,
    Study,
    StudyAnnotator,
)


log = logging.getLogger(__name__)


# ExposureRoute / ExposureType rows are get-or-created from the incoming
# {term_uri, term_label} payload. No server-side ontology validation in
# this pass — the client is expected to submit a term it picked via an
# autocomplete against the relevant ontology.
_ONTOLOGY_FIELD_ORM = {
    "route": ExposureRoute,
    "exposure_type": ExposureType,
}


def _resolve_ontology_term(session: Session, field_name: str, payload):
    if payload is None:
        return None

    orm_cls = _ONTOLOGY_FIELD_ORM[field_name]
    term_uri = payload.term_uri
    term_label = payload.term_label

    existing = (
        session.query(orm_cls).filter(orm_cls.term_uri == term_uri).one_or_none()
    )
    if existing is not None:
        # Backfill label if the stored row was created with a placeholder.
        if term_label and existing.term_label != term_label:
            existing.term_label = term_label
        return existing
    new = orm_cls(term_uri=term_uri, term_label=term_label)
    session.add(new)
    return new


def _get_or_create_by_attrs(session: Session, model, /, **attrs):
    """Best-effort get-or-create helper.

    We intentionally keep this simple because the schema/ORM may still be in
    flux (and may move into this repository).
    """

    instance = session.query(model).filter_by(**attrs).one_or_none()
    if instance is not None:
        return instance
    instance = model(**attrs)
    session.add(instance)
    return instance


def _quantity_value_from_payload(payload: QuantityValue | None) -> QuantityValue | None:
    if payload is None:
        return None
    # QuantityValue is both a Pydantic model and an ORM class name; here we
    # assume payload is the Pydantic version and construct ORM version.
    return QuantityValue(
        unit=getattr(payload, "unit", None),
        numeric_value=getattr(payload, "numeric_value", None),
    )


def _fish_from_payload(session: Session, payload: Fish | None) -> Fish | None:
    if payload is None:
        return None
    # Fish has a natural identifier (zfin_id). Prefer upsert semantics.
    try:
        return _get_or_create_by_attrs(session, Fish, zfin_id=payload.zfin_id, name=payload.name)
    except Exception:
        # Fall back to naive instance creation if constraints differ.
        return Fish(zfin_id=payload.zfin_id, name=payload.name)


def _phenotype_term_from_payload(session: Session, payload: PhenotypeTerm | None) -> PhenotypeTerm | None:
    if payload is None:
        return None
    # ``PhenotypeTerm`` has a composite PK ``(term_uri, term_label)`` but
    # ``Phenotype.phenotype_term_id`` FKs to ``term_uri`` only. If we naïvely
    # created a second row with the same ``term_uri`` and a different label
    # (e.g. a curator pasting just the CURIE) existing FKs become ambiguous
    # and SQLAlchemy's relationship resolver picks one at random. Always
    # reuse an existing row keyed on ``term_uri`` — upgrade its label only
    # if the current one is empty and the payload carries something real.
    incoming_label = getattr(payload, "term_label", None) or ""
    existing = (
        session.query(PhenotypeTerm)
        .filter(PhenotypeTerm.term_uri == payload.term_uri)
        .first()
    )
    if existing is not None:
        return existing
    label = incoming_label or payload.term_uri  # term_label is NOT NULL
    return PhenotypeTerm(term_uri=payload.term_uri, term_label=label)


def _chemical_entity_from_payload(session: Session, payload: ChemicalEntity | None) -> ChemicalEntity | None:
    if payload is None:
        return None

    # NOTE: Depending on the ORM primary key definition, this may need
    # adjustment. This is intentionally best-effort.
    attrs = {
        "uri": payload.uri,
        "chebi_id": getattr(payload, "chebi_id", None),
        "cas_id": getattr(payload, "cas_id", None),
        "chemical_name": getattr(payload, "chemical_name", None),
    }
    try:
        return _get_or_create_by_attrs(session, ChemicalEntity, **attrs)
    except Exception:
        return ChemicalEntity(**attrs)


def _stressor_from_create(session: Session, payload: StressorChemicalCreate) -> StressorChemical:
    chemical = _chemical_entity_from_payload(session, payload.chemical_id)
    concentration = _quantity_value_from_payload(payload.concentration)
    return StressorChemical(
        chemical_id=chemical,
        concentration=concentration,
        manufacturer=payload.manufacturer,
        comment=getattr(payload, "comment", None),
    )


def _phenotype_from_create(session: Session, payload: PhenotypeCreate) -> Phenotype:
    prevalence = _quantity_value_from_payload(getattr(payload, "prevalence", None))
    phenotype_term = _phenotype_term_from_payload(session, getattr(payload, "phenotype_term_id", None))
    return Phenotype(
        stage=payload.stage,
        severity=getattr(payload, "severity", None),
        prevalence=prevalence,
        phenotype_term_id=phenotype_term,
    )


def _obs_set_from_create(session: Session, payload: PhenotypeObservationSetCreate) -> PhenotypeObservationSet:
    obs = PhenotypeObservationSet()
    for ph in payload.phenotype or []:
        obs.phenotype.append(_phenotype_from_create(session, ph))
    # Images and control images intentionally omitted for now.
    return obs


def _regimen_from_create(session: Session, payload: RegimenCreate | None) -> Regimen | None:
    if payload is None:
        return None
    return Regimen(
        exposure_regimen_type=getattr(payload, "exposure_regimen_type", None),
        number_of_individual_exposure=getattr(payload, "number_of_individual_exposure", None),
        interval_between_individual_exposures=_quantity_value_from_payload(
            getattr(payload, "interval_between_individual_exposures", None)
        ),
        total_exposure_duration=_quantity_value_from_payload(getattr(payload, "total_exposure_duration", None)),
        individual_exposure_duration=_quantity_value_from_payload(
            getattr(payload, "individual_exposure_duration", None)
        ),
    )


def _exposure_event_from_create(session: Session, payload: ExposureEventCreate) -> ExposureEvent:
    ee = ExposureEvent(
        route=_resolve_ontology_term(session, "route", payload.route),
        exposure_start_stage=payload.exposure_start_stage,
        exposure_end_stage=payload.exposure_end_stage,
        comment=getattr(payload, "comment", None),
        exposure_type=_resolve_ontology_term(
            session, "exposure_type", getattr(payload, "exposure_type", None)
        ),
        additional_exposure_condition=getattr(payload, "additional_exposure_condition", None),
        regimen=_regimen_from_create(session, getattr(payload, "regimen", None)),
    )
    if payload.vehicle:
        ee.vehicle = list(payload.vehicle)
    for s in payload.stressor or []:
        ee.stressor.append(_stressor_from_create(session, s))
    for obs in payload.phenotype_observation or []:
        ee.phenotype_observation.append(_obs_set_from_create(session, obs))
    return ee


def _control_from_create(payload: ControlCreate) -> Control:
    return Control(
        control_type=payload.control_type,
        vehicle_if_treated=getattr(payload, "vehicle_if_treated", None),
        comment=getattr(payload, "comment", None),
    )


def _experiment_from_create(session: Session, payload: ExperimentCreate) -> Experiment:
    exp = Experiment(
        standard_rearing_condition=payload.standard_rearing_condition,
        rearing_condition_comment=getattr(payload, "rearing_condition_comment", None),
        fish=_fish_from_payload(session, getattr(payload, "fish", None)),
    )
    for c in payload.control or []:
        exp.control.append(_control_from_create(c))
    for ee in payload.exposure_event or []:
        exp.exposure_event.append(_exposure_event_from_create(session, ee))
    return exp


def _study_from_create(session: Session, payload: StudyCreate) -> Study:
    study = Study(
        publication=payload.publication,
        lab=payload.lab,
    )
    # association_proxy list assignment should work for annotator
    if payload.annotator is not None:
        study.annotator = payload.annotator
    for exp_payload in payload.experiment or []:
        study.experiment.append(_experiment_from_create(session, exp_payload))
    return study


def create_study(session: Session, payload: StudyCreate) -> Study:
    study = _study_from_create(session, payload)
    session.add(study)
    session.commit()
    session.refresh(study)
    return study


def get_study_by_id(session: Session, study_id: int) -> Optional[Study]:
    # SQLAlchemy 1.4/2.0: Session.get is preferred.
    try:
        return session.get(Study, study_id)
    except Exception:
        return session.query(Study).filter(Study.id == study_id).one_or_none()


def list_studies(session: Session, *, limit: int = 50, offset: int = 0) -> list[Study]:
    q = session.query(Study).order_by(Study.id).offset(offset).limit(limit)
    return list(q)


def delete_study(session: Session, study_id: int, *, storage) -> bool:
    # Lazy import to avoid a cycle with experiments → studies.
    from server.api.services.experiments import delete_experiment_row

    study = get_study_by_id(session, study_id)
    if study is None:
        return False
    for experiment in list(study.experiment or []):
        delete_experiment_row(session, experiment, storage=storage)
    # Study_annotator assoc rows (no cascade on the generated relationship)
    session.query(StudyAnnotator).filter_by(
        Study_id=study.id
    ).delete(synchronize_session="fetch")
    session.delete(study)
    session.commit()
    return True


def patch_study(session: Session, study_id: int, patch: StudyUpdate) -> Optional[Study]:
    study = get_study_by_id(session, study_id)
    if study is None:
        return None

    # NOTE: This is deliberately a shallow patch for now.
    if patch.publication is not None:
        study.publication = patch.publication
    if patch.lab is not None:
        study.lab = patch.lab
    if patch.annotator is not None:
        # The annotator_rel relationship doesn't have `cascade="all,
        # delete-orphan"` (generator gap — tracked on the schema repo),
        # so reassigning the association_proxy triggers a NULLify on the
        # composite-PK child rows and crashes. Delete the rows at the
        # SQL layer, expire the relationship, then append the new list.
        session.query(StudyAnnotator).filter(
            StudyAnnotator.Study_id == study.id
        ).delete(synchronize_session="fetch")
        session.flush()
        session.expire(study, ["annotator_rel"])
        for a in patch.annotator:
            study.annotator.append(a)

    session.commit()
    session.refresh(study)
    return study
