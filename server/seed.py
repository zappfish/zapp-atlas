"""Dev seed data. Idempotent — safe to run multiple times.

Populates a small set of Study/Experiment/Exposure/Observation records so the
UI has something to render on first boot.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from server.db import get_engine, get_session_factory, init_db
from zebrafish_toxicology_atlas_schema.datamodel.sqla import (  # type: ignore
    ChemicalEntity,
    ExposureEvent,
    ExposureRoute,
    ExposureType,
    Experiment,
    Fish,
    Phenotype,
    PhenotypeObservationSet,
    PhenotypeTerm,
    QuantityValue,
    StressorChemical,
    Study,
)


SEEDED_PUBLICATIONS = {
    "PMID:22194820",
    "DOI:10.1234/seed.example.002",
}


def _upsert_fish(session: Session, *, zfin_id: str, name: str) -> Fish:
    fish = session.query(Fish).filter_by(zfin_id=zfin_id).one_or_none()
    if fish is None:
        fish = Fish(zfin_id=zfin_id, name=name)
        session.add(fish)
    return fish


def _upsert_phenotype_term(session: Session, *, term_uri: str, term_label: str) -> PhenotypeTerm:
    term = session.query(PhenotypeTerm).filter_by(term_uri=term_uri).one_or_none()
    if term is None:
        term = PhenotypeTerm(term_uri=term_uri, term_label=term_label)
        session.add(term)
    return term


def _upsert_exposure_route(
    session: Session, *, term_uri: str, term_label: str
) -> ExposureRoute:
    term = session.query(ExposureRoute).filter_by(term_uri=term_uri).one_or_none()
    if term is None:
        term = ExposureRoute(term_uri=term_uri, term_label=term_label)
        session.add(term)
    return term


def _upsert_exposure_type(
    session: Session, *, term_uri: str, term_label: str
) -> ExposureType:
    term = session.query(ExposureType).filter_by(term_uri=term_uri).one_or_none()
    if term is None:
        term = ExposureType(term_uri=term_uri, term_label=term_label)
        session.add(term)
    return term


def _build_bpa_study(session: Session) -> Study:
    fish = _upsert_fish(session, zfin_id="ZFIN:ZDB-GENO-960809-7", name="AB")
    bpa = ChemicalEntity(
        uri="http://purl.obolibrary.org/obo/CHEBI_33216",
        chebi_id="CHEBI:33216",
        cas_id="80-05-7",
        chemical_name="bisphenol A",
    )
    pericardial_edema = _upsert_phenotype_term(
        session,
        term_uri="ZP:0105827",
        term_label="pericardial region edematous, abnormal",
    )

    study = Study(
        publication="PMID:22194820",
        lab="ZFIN:ZDB-LAB-0001-01",
        annotator=["ORCID:0000-0001-0101-0101"],
    )

    water_route = _upsert_exposure_route(
        session, term_uri="ExO:0000057", term_label="water exposure"
    )
    continuous = _upsert_exposure_type(
        session, term_uri="ExO:0000109", term_label="continuous exposure"
    )

    experiment = Experiment(standard_rearing_condition=True, fish=fish)
    study.experiment.append(experiment)

    exposure = ExposureEvent(
        route=water_route,
        exposure_start_stage="ZFS:0000011",
        exposure_end_stage="ZFS:0000039",
        exposure_type=continuous,
    )
    experiment.exposure_event.append(exposure)

    exposure.stressor.append(
        StressorChemical(
            chemical_id=bpa,
            concentration=QuantityValue(unit="µg/L", numeric_value="100"),
            manufacturer="Sigma-Aldrich",
        )
    )

    obs = PhenotypeObservationSet()
    exposure.phenotype_observation.append(obs)
    obs.phenotype.append(
        Phenotype(
            stage="ZFS:0000035",
            severity="moderate",
            phenotype_term_id=pericardial_edema,
        )
    )

    return study


def _build_cyclopamine_study(session: Session) -> Study:
    fish = _upsert_fish(session, zfin_id="ZFIN:ZDB-GENO-010112-1", name="TU")
    cyclopamine = ChemicalEntity(
        uri="http://purl.obolibrary.org/obo/CHEBI_4023",
        chebi_id="CHEBI:4023",
        cas_id="4449-51-8",
        chemical_name="cyclopamine",
    )
    cyclopia = _upsert_phenotype_term(
        session,
        term_uri="ZP:0002137",
        term_label="cyclopia",
    )

    study = Study(
        publication="DOI:10.1234/seed.example.002",
        lab="ZFIN:ZDB-LAB-0002-02",
        annotator=["ORCID:0000-0002-0202-0202"],
    )

    water_route = _upsert_exposure_route(
        session, term_uri="ExO:0000057", term_label="water exposure"
    )
    continuous = _upsert_exposure_type(
        session, term_uri="ExO:0000109", term_label="continuous exposure"
    )

    experiment = Experiment(standard_rearing_condition=True, fish=fish)
    study.experiment.append(experiment)

    exposure = ExposureEvent(
        route=water_route,
        exposure_start_stage="ZFS:0000013",
        exposure_end_stage="ZFS:0000025",
        exposure_type=continuous,
    )
    experiment.exposure_event.append(exposure)

    exposure.stressor.append(
        StressorChemical(
            chemical_id=cyclopamine,
            concentration=QuantityValue(unit="µM", numeric_value="5"),
        )
    )

    obs = PhenotypeObservationSet()
    exposure.phenotype_observation.append(obs)
    obs.phenotype.append(
        Phenotype(stage="ZFS:0000025", severity="severe", phenotype_term_id=cyclopia)
    )

    return study


def seed(session: Session) -> None:
    """Seed the database with demo data. Idempotent on `Study.publication`."""

    existing = {
        pub
        for (pub,) in session.query(Study.publication).filter(
            Study.publication.in_(SEEDED_PUBLICATIONS)
        )
    }

    builders = {
        "PMID:22194820": _build_bpa_study,
        "DOI:10.1234/seed.example.002": _build_cyclopamine_study,
    }

    for pub, builder in builders.items():
        if pub in existing:
            continue
        session.add(builder(session))

    session.commit()


def main() -> None:
    engine = get_engine()
    init_db(engine)
    Session = get_session_factory(engine)
    with Session() as session:
        seed(session)
    print("Seeded.")


if __name__ == "__main__":
    main()
