from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from zebrafish_toxicology_atlas_schema.datamodel import sqla
from zebrafish_toxicology_atlas_schema.datamodel.pydanticmodel_v2 import (
    # Create models
    StudyCreate,
    ExperimentCreate,
    ExposureEventCreate,
    StressorChemicalCreate,
    PhenotypeObservationSetCreate,
    PhenotypeCreate,
    ControlCreate,
    RegimenCreate,
    ImageCreate,
    ControlImageCreate,
    # Update models
    StudyUpdate,
    ExperimentUpdate,
    ExposureEventUpdate,
    StressorChemicalUpdate,
    PhenotypeObservationSetUpdate,
    PhenotypeUpdate,
    ControlUpdate,
    RegimenUpdate,
    ImageUpdate,
    ControlImageUpdate,
    # Read models
    StudyRead,
    ExperimentRead,
    ExposureEventRead,
    StressorChemicalRead,
    PhenotypeObservationSetRead,
    PhenotypeRead,
    ControlRead,
    RegimenRead,
    ImageRead,
    ControlImageRead,
    ChemicalEntityRead,
    PhenotypeTermRead,
    FishRead,
    QuantityValueRead,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Conversion helpers
# ---------------------------------------------------------------------------

def pydantic_to_sqla(obj, sqla_class):
    """Recursively convert a Pydantic Create model to a SQLAlchemy model."""
    data = obj if isinstance(obj, dict) else obj.model_dump()

    nested_relations = {
        "experiment": (sqla.Experiment, True),
        "fish": (sqla.Fish, False),
        "control": (sqla.Control, True),
        "exposure_event": (sqla.ExposureEvent, True),
        "stressor": (sqla.StressorChemical, True),
        "phenotype_observation": (sqla.PhenotypeObservationSet, True),
        "regimen": (sqla.Regimen, False),
        "chemical_id": (sqla.ChemicalEntity, False),
        "concentration": (sqla.QuantityValue, False),
        "phenotype": (sqla.Phenotype, True),
        "image": (sqla.Image, True),
        "control_image": (sqla.ControlImage, True),
        "phenotype_term_id": (sqla.PhenotypeTerm, False),
        "prevalence": (sqla.QuantityValue, False),
        "interval_between_individual_exposures": (sqla.QuantityValue, False),
        "total_exposure_duration": (sqla.QuantityValue, False),
        "individual_exposure_duration": (sqla.QuantityValue, False),
    }

    kwargs = {}
    for key, value in data.items():
        if value is None:
            continue
        if key in nested_relations:
            rel_class, is_list = nested_relations[key]
            if is_list:
                kwargs[key] = [pydantic_to_sqla(item, rel_class) for item in value]
            else:
                kwargs[key] = pydantic_to_sqla(value, rel_class)
        elif key == "annotator" and isinstance(value, list):
            continue  # handled after construction via association proxy
        else:
            kwargs[key] = value

    instance = sqla_class(**kwargs)

    if hasattr(instance, "annotator") and "annotator" in data:
        annotator_val = data["annotator"]
        if isinstance(annotator_val, list) and annotator_val:
            for a in annotator_val:
                instance.annotator.append(a)

    return instance


# ---------------------------------------------------------------------------
# Generic CRUD helpers for ZappEntity subclasses (integer PK)
# ---------------------------------------------------------------------------

def _create_entity(db: Session, sqla_class, create_obj):
    instance = pydantic_to_sqla(create_obj, sqla_class)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


def _list_entities(db: Session, sqla_class):
    return db.query(sqla_class).all()


def _get_entity(db: Session, sqla_class, entity_id: int):
    instance = db.get(sqla_class, entity_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Not found")
    return instance


def _update_entity(db: Session, sqla_class, entity_id: int, update_obj):
    instance = db.get(sqla_class, entity_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Not found")
    update_data = update_obj.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "annotator":
            instance.annotator_rel.clear()
            for a in value:
                instance.annotator.append(a)
        else:
            setattr(instance, key, value)
    db.commit()
    db.refresh(instance)
    return instance


def _delete_entity(db: Session, sqla_class, entity_id: int):
    instance = db.get(sqla_class, entity_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(instance)
    db.commit()
    return {"ok": True}


# ---------------------------------------------------------------------------
# Study CRUD
# ---------------------------------------------------------------------------

@router.post("/studies", response_model=StudyRead)
def create_study(body: StudyCreate, db: Session = Depends(get_db)):
    return _create_entity(db, sqla.Study, body)


@router.get("/studies", response_model=list[StudyRead])
def list_studies(db: Session = Depends(get_db)):
    return _list_entities(db, sqla.Study)


@router.get("/studies/{study_id}", response_model=StudyRead)
def get_study(study_id: int, db: Session = Depends(get_db)):
    return _get_entity(db, sqla.Study, study_id)


@router.patch("/studies/{study_id}", response_model=StudyRead)
def update_study(study_id: int, body: StudyUpdate, db: Session = Depends(get_db)):
    return _update_entity(db, sqla.Study, study_id, body)


@router.delete("/studies/{study_id}")
def delete_study(study_id: int, db: Session = Depends(get_db)):
    return _delete_entity(db, sqla.Study, study_id)


# ---------------------------------------------------------------------------
# Experiment CRUD
# ---------------------------------------------------------------------------

@router.post("/experiments", response_model=ExperimentRead)
def create_experiment(body: ExperimentCreate, db: Session = Depends(get_db)):
    return _create_entity(db, sqla.Experiment, body)


@router.get("/experiments", response_model=list[ExperimentRead])
def list_experiments(db: Session = Depends(get_db)):
    return _list_entities(db, sqla.Experiment)


@router.get("/experiments/{experiment_id}", response_model=ExperimentRead)
def get_experiment(experiment_id: int, db: Session = Depends(get_db)):
    return _get_entity(db, sqla.Experiment, experiment_id)


@router.patch("/experiments/{experiment_id}", response_model=ExperimentRead)
def update_experiment(experiment_id: int, body: ExperimentUpdate, db: Session = Depends(get_db)):
    return _update_entity(db, sqla.Experiment, experiment_id, body)


@router.delete("/experiments/{experiment_id}")
def delete_experiment(experiment_id: int, db: Session = Depends(get_db)):
    return _delete_entity(db, sqla.Experiment, experiment_id)


# ---------------------------------------------------------------------------
# ExposureEvent CRUD
# ---------------------------------------------------------------------------

@router.post("/exposure-events", response_model=ExposureEventRead)
def create_exposure_event(body: ExposureEventCreate, db: Session = Depends(get_db)):
    return _create_entity(db, sqla.ExposureEvent, body)


@router.get("/exposure-events", response_model=list[ExposureEventRead])
def list_exposure_events(db: Session = Depends(get_db)):
    return _list_entities(db, sqla.ExposureEvent)


@router.get("/exposure-events/{event_id}", response_model=ExposureEventRead)
def get_exposure_event(event_id: int, db: Session = Depends(get_db)):
    return _get_entity(db, sqla.ExposureEvent, event_id)


@router.patch("/exposure-events/{event_id}", response_model=ExposureEventRead)
def update_exposure_event(event_id: int, body: ExposureEventUpdate, db: Session = Depends(get_db)):
    return _update_entity(db, sqla.ExposureEvent, event_id, body)


@router.delete("/exposure-events/{event_id}")
def delete_exposure_event(event_id: int, db: Session = Depends(get_db)):
    return _delete_entity(db, sqla.ExposureEvent, event_id)


# ---------------------------------------------------------------------------
# StressorChemical CRUD
# ---------------------------------------------------------------------------

@router.post("/stressor-chemicals", response_model=StressorChemicalRead)
def create_stressor_chemical(body: StressorChemicalCreate, db: Session = Depends(get_db)):
    return _create_entity(db, sqla.StressorChemical, body)


@router.get("/stressor-chemicals", response_model=list[StressorChemicalRead])
def list_stressor_chemicals(db: Session = Depends(get_db)):
    return _list_entities(db, sqla.StressorChemical)


@router.get("/stressor-chemicals/{sc_id}", response_model=StressorChemicalRead)
def get_stressor_chemical(sc_id: int, db: Session = Depends(get_db)):
    return _get_entity(db, sqla.StressorChemical, sc_id)


@router.patch("/stressor-chemicals/{sc_id}", response_model=StressorChemicalRead)
def update_stressor_chemical(sc_id: int, body: StressorChemicalUpdate, db: Session = Depends(get_db)):
    return _update_entity(db, sqla.StressorChemical, sc_id, body)


@router.delete("/stressor-chemicals/{sc_id}")
def delete_stressor_chemical(sc_id: int, db: Session = Depends(get_db)):
    return _delete_entity(db, sqla.StressorChemical, sc_id)


# ---------------------------------------------------------------------------
# PhenotypeObservationSet CRUD
# ---------------------------------------------------------------------------

@router.post("/phenotype-observation-sets", response_model=PhenotypeObservationSetRead)
def create_phenotype_observation_set(body: PhenotypeObservationSetCreate, db: Session = Depends(get_db)):
    return _create_entity(db, sqla.PhenotypeObservationSet, body)


@router.get("/phenotype-observation-sets", response_model=list[PhenotypeObservationSetRead])
def list_phenotype_observation_sets(db: Session = Depends(get_db)):
    return _list_entities(db, sqla.PhenotypeObservationSet)


@router.get("/phenotype-observation-sets/{pos_id}", response_model=PhenotypeObservationSetRead)
def get_phenotype_observation_set(pos_id: int, db: Session = Depends(get_db)):
    return _get_entity(db, sqla.PhenotypeObservationSet, pos_id)


@router.patch("/phenotype-observation-sets/{pos_id}", response_model=PhenotypeObservationSetRead)
def update_phenotype_observation_set(pos_id: int, body: PhenotypeObservationSetUpdate, db: Session = Depends(get_db)):
    return _update_entity(db, sqla.PhenotypeObservationSet, pos_id, body)


@router.delete("/phenotype-observation-sets/{pos_id}")
def delete_phenotype_observation_set(pos_id: int, db: Session = Depends(get_db)):
    return _delete_entity(db, sqla.PhenotypeObservationSet, pos_id)


# ---------------------------------------------------------------------------
# Phenotype CRUD
# ---------------------------------------------------------------------------

@router.post("/phenotypes", response_model=PhenotypeRead)
def create_phenotype(body: PhenotypeCreate, db: Session = Depends(get_db)):
    return _create_entity(db, sqla.Phenotype, body)


@router.get("/phenotypes", response_model=list[PhenotypeRead])
def list_phenotypes(db: Session = Depends(get_db)):
    return _list_entities(db, sqla.Phenotype)


@router.get("/phenotypes/{phenotype_id}", response_model=PhenotypeRead)
def get_phenotype(phenotype_id: int, db: Session = Depends(get_db)):
    return _get_entity(db, sqla.Phenotype, phenotype_id)


@router.patch("/phenotypes/{phenotype_id}", response_model=PhenotypeRead)
def update_phenotype(phenotype_id: int, body: PhenotypeUpdate, db: Session = Depends(get_db)):
    return _update_entity(db, sqla.Phenotype, phenotype_id, body)


@router.delete("/phenotypes/{phenotype_id}")
def delete_phenotype(phenotype_id: int, db: Session = Depends(get_db)):
    return _delete_entity(db, sqla.Phenotype, phenotype_id)


# ---------------------------------------------------------------------------
# Control CRUD
# ---------------------------------------------------------------------------

@router.post("/controls", response_model=ControlRead)
def create_control(body: ControlCreate, db: Session = Depends(get_db)):
    return _create_entity(db, sqla.Control, body)


@router.get("/controls", response_model=list[ControlRead])
def list_controls(db: Session = Depends(get_db)):
    return _list_entities(db, sqla.Control)


@router.get("/controls/{control_id}", response_model=ControlRead)
def get_control(control_id: int, db: Session = Depends(get_db)):
    return _get_entity(db, sqla.Control, control_id)


@router.patch("/controls/{control_id}", response_model=ControlRead)
def update_control(control_id: int, body: ControlUpdate, db: Session = Depends(get_db)):
    return _update_entity(db, sqla.Control, control_id, body)


@router.delete("/controls/{control_id}")
def delete_control(control_id: int, db: Session = Depends(get_db)):
    return _delete_entity(db, sqla.Control, control_id)


# ---------------------------------------------------------------------------
# Regimen CRUD
# ---------------------------------------------------------------------------

@router.post("/regimens", response_model=RegimenRead)
def create_regimen(body: RegimenCreate, db: Session = Depends(get_db)):
    return _create_entity(db, sqla.Regimen, body)


@router.get("/regimens", response_model=list[RegimenRead])
def list_regimens(db: Session = Depends(get_db)):
    return _list_entities(db, sqla.Regimen)


@router.get("/regimens/{regimen_id}", response_model=RegimenRead)
def get_regimen(regimen_id: int, db: Session = Depends(get_db)):
    return _get_entity(db, sqla.Regimen, regimen_id)


@router.patch("/regimens/{regimen_id}", response_model=RegimenRead)
def update_regimen(regimen_id: int, body: RegimenUpdate, db: Session = Depends(get_db)):
    return _update_entity(db, sqla.Regimen, regimen_id, body)


@router.delete("/regimens/{regimen_id}")
def delete_regimen(regimen_id: int, db: Session = Depends(get_db)):
    return _delete_entity(db, sqla.Regimen, regimen_id)


# ---------------------------------------------------------------------------
# Image CRUD
# ---------------------------------------------------------------------------

@router.post("/images", response_model=ImageRead)
def create_image(body: ImageCreate, db: Session = Depends(get_db)):
    return _create_entity(db, sqla.Image, body)


@router.get("/images", response_model=list[ImageRead])
def list_images(db: Session = Depends(get_db)):
    return _list_entities(db, sqla.Image)


@router.get("/images/{image_id}", response_model=ImageRead)
def get_image(image_id: int, db: Session = Depends(get_db)):
    return _get_entity(db, sqla.Image, image_id)


@router.patch("/images/{image_id}", response_model=ImageRead)
def update_image(image_id: int, body: ImageUpdate, db: Session = Depends(get_db)):
    return _update_entity(db, sqla.Image, image_id, body)


@router.delete("/images/{image_id}")
def delete_image(image_id: int, db: Session = Depends(get_db)):
    return _delete_entity(db, sqla.Image, image_id)


# ---------------------------------------------------------------------------
# ControlImage CRUD
# ---------------------------------------------------------------------------

@router.post("/control-images", response_model=ControlImageRead)
def create_control_image(body: ControlImageCreate, db: Session = Depends(get_db)):
    return _create_entity(db, sqla.ControlImage, body)


@router.get("/control-images", response_model=list[ControlImageRead])
def list_control_images(db: Session = Depends(get_db)):
    return _list_entities(db, sqla.ControlImage)


@router.get("/control-images/{ci_id}", response_model=ControlImageRead)
def get_control_image(ci_id: int, db: Session = Depends(get_db)):
    return _get_entity(db, sqla.ControlImage, ci_id)


@router.patch("/control-images/{ci_id}", response_model=ControlImageRead)
def update_control_image(ci_id: int, body: ControlImageUpdate, db: Session = Depends(get_db)):
    return _update_entity(db, sqla.ControlImage, ci_id, body)


@router.delete("/control-images/{ci_id}")
def delete_control_image(ci_id: int, db: Session = Depends(get_db)):
    return _delete_entity(db, sqla.ControlImage, ci_id)


# ---------------------------------------------------------------------------
# Reference entity CRUD (non-integer PKs)
# ---------------------------------------------------------------------------

# -- ChemicalEntity (PK: uri) ----------------------------------------------

@router.post("/chemical-entities", response_model=ChemicalEntityRead)
def create_chemical_entity(body: ChemicalEntityRead, db: Session = Depends(get_db)):
    instance = sqla.ChemicalEntity(**body.model_dump())
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


@router.get("/chemical-entities", response_model=list[ChemicalEntityRead])
def list_chemical_entities(db: Session = Depends(get_db)):
    return db.query(sqla.ChemicalEntity).all()


@router.get("/chemical-entities/{uri:path}", response_model=ChemicalEntityRead)
def get_chemical_entity(uri: str, db: Session = Depends(get_db)):
    instance = db.get(sqla.ChemicalEntity, uri)
    if not instance:
        raise HTTPException(status_code=404, detail="Not found")
    return instance


@router.delete("/chemical-entities/{uri:path}")
def delete_chemical_entity(uri: str, db: Session = Depends(get_db)):
    instance = db.get(sqla.ChemicalEntity, uri)
    if not instance:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(instance)
    db.commit()
    return {"ok": True}


# -- PhenotypeTerm (PK: term_uri) ------------------------------------------

@router.post("/phenotype-terms", response_model=PhenotypeTermRead)
def create_phenotype_term(body: PhenotypeTermRead, db: Session = Depends(get_db)):
    instance = sqla.PhenotypeTerm(**body.model_dump())
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


@router.get("/phenotype-terms", response_model=list[PhenotypeTermRead])
def list_phenotype_terms(db: Session = Depends(get_db)):
    return db.query(sqla.PhenotypeTerm).all()


@router.get("/phenotype-terms/{term_uri:path}", response_model=PhenotypeTermRead)
def get_phenotype_term(term_uri: str, db: Session = Depends(get_db)):
    instance = db.get(sqla.PhenotypeTerm, term_uri)
    if not instance:
        raise HTTPException(status_code=404, detail="Not found")
    return instance


@router.delete("/phenotype-terms/{term_uri:path}")
def delete_phenotype_term(term_uri: str, db: Session = Depends(get_db)):
    instance = db.get(sqla.PhenotypeTerm, term_uri)
    if not instance:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(instance)
    db.commit()
    return {"ok": True}


# -- Fish (PK: zfin_id) ----------------------------------------------------

@router.post("/fish", response_model=FishRead)
def create_fish(body: FishRead, db: Session = Depends(get_db)):
    instance = sqla.Fish(**body.model_dump())
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


@router.get("/fish", response_model=list[FishRead])
def list_fish(db: Session = Depends(get_db)):
    return db.query(sqla.Fish).all()


@router.get("/fish/{zfin_id}", response_model=FishRead)
def get_fish(zfin_id: str, db: Session = Depends(get_db)):
    instance = db.get(sqla.Fish, zfin_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Not found")
    return instance


@router.delete("/fish/{zfin_id}")
def delete_fish(zfin_id: str, db: Session = Depends(get_db)):
    instance = db.get(sqla.Fish, zfin_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(instance)
    db.commit()
    return {"ok": True}
