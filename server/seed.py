"""Dev seed data. Idempotent — safe to run multiple times.

Each builder function corresponds to one real, published zebrafish
toxicology study curated into our schema. The CURIEs and labels used
match their canonical ontology terms (EXO / ECTO / ChEBI / ZP / ZFIN)
so curators see realistic examples and so the detail view exercises
the label-resolution path.

Currently seeded:

* **Lam et al. 2011** (PMID:22194820) — BPA embryotoxicity in AB.
* **Nishi et al. 2025** (PMID:40359302) — BPA + retinoic acid co-exposure
  potentiates neural crest + hindbrain defects; AB background.
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
    "PMID:40359302",
}


# ---------------------------------------------------------------------------
# Upsert helpers
# ---------------------------------------------------------------------------


def _upsert_chemical(
    session: Session,
    *,
    uri: str,
    chebi_id: str,
    cas_id: str,
    chemical_name: str,
) -> ChemicalEntity:
    existing = (
        session.query(ChemicalEntity)
        .filter_by(
            uri=uri,
            chebi_id=chebi_id,
            cas_id=cas_id,
            chemical_name=chemical_name,
        )
        .one_or_none()
    )
    if existing is not None:
        return existing
    chemical = ChemicalEntity(
        uri=uri,
        chebi_id=chebi_id,
        cas_id=cas_id,
        chemical_name=chemical_name,
    )
    session.add(chemical)
    return chemical


def _upsert_fish(session: Session, *, zfin_id: str, name: str) -> Fish:
    fish = session.query(Fish).filter_by(zfin_id=zfin_id).one_or_none()
    if fish is None:
        fish = Fish(zfin_id=zfin_id, name=name)
        session.add(fish)
    return fish


def _upsert_phenotype_term(
    session: Session, *, term_uri: str, term_label: str
) -> PhenotypeTerm:
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


# Shared route / type terms. Both seeded studies use standard water-immersion
# exposure of developing embryos.
def _aquatic_route(session: Session) -> ExposureRoute:
    return _upsert_exposure_route(
        session,
        term_uri="ExO:0000161",
        term_label="ambient acquatic environment route",
    )


# ---------------------------------------------------------------------------
# Studies
# ---------------------------------------------------------------------------


def _build_bpa_study(session: Session) -> Study:
    """Lam et al. 2011 — `Molecular conservation of estrogen-response
    associated with cell cycle regulation, hormonal carcinogenesis and
    cancer in zebrafish and human cancer cell lines.` BPA alone on AB
    embryos produces pericardial edema at 72 hpf.
    """

    fish = _upsert_fish(session, zfin_id="ZFIN:ZDB-GENO-960809-7", name="AB")
    bpa = _upsert_chemical(
        session,
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

    route = _aquatic_route(session)
    exposure_type = _upsert_exposure_type(
        session,
        term_uri="ECTO:9000057",
        term_label="exposure to bisphenol A",
    )

    experiment = Experiment(standard_rearing_condition=True, fish=fish)
    study.experiment.append(experiment)

    exposure = ExposureEvent(
        route=route,
        exposure_start_stage="ZFS:0000011",
        exposure_end_stage="ZFS:0000039",
        exposure_type=exposure_type,
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
            prevalence=QuantityValue(unit="%", numeric_value="60"),
        )
    )

    return study


def _build_nishi_bpa_ra_study(session: Session) -> Study:
    """Nishi et al. 2025 — `Effects of Bisphenol A and Retinoic Acid Exposure
    on Neuron and Brain Formation` (EHP, PMID:40359302). BPA potentiates
    retinoic-acid-induced hindbrain disorganization, Mauthner-cell
    duplication, and craniofacial cartilage anomalies. Co-exposure on AB
    embryos from dome stage (ZFS:0000013) through hatching-day larva.
    """

    fish = _upsert_fish(session, zfin_id="ZFIN:ZDB-GENO-960809-7", name="AB")
    bpa = _upsert_chemical(
        session,
        uri="http://purl.obolibrary.org/obo/CHEBI_33216",
        chebi_id="CHEBI:33216",
        cas_id="80-05-7",
        chemical_name="bisphenol A",
    )
    retinoic_acid = _upsert_chemical(
        session,
        uri="http://purl.obolibrary.org/obo/CHEBI_15367",
        chebi_id="CHEBI:15367",
        cas_id="302-79-4",
        chemical_name="all-trans-retinoic acid",
    )

    head_abnormal = _upsert_phenotype_term(
        session,
        term_uri="ZP:0001609",
        term_label="head morphology, abnormal",
    )

    study = Study(
        publication="PMID:40359302",
        lab="ZFIN:ZDB-LAB-0003-01",
        annotator=["ORCID:0000-0003-0303-0303"],
    )

    route = _aquatic_route(session)
    exposure_type = _upsert_exposure_type(
        session,
        term_uri="ECTO:9000057",
        term_label="exposure to bisphenol A",
    )

    experiment = Experiment(standard_rearing_condition=True, fish=fish)
    study.experiment.append(experiment)

    exposure = ExposureEvent(
        route=route,
        exposure_start_stage="ZFS:0000013",
        exposure_end_stage="ZFS:0000050",
        exposure_type=exposure_type,
        comment="BPA + retinoic acid co-exposure; RA potentiation observed.",
    )
    experiment.exposure_event.append(exposure)

    exposure.stressor.append(
        StressorChemical(
            chemical_id=bpa,
            concentration=QuantityValue(unit="µM", numeric_value="10"),
        )
    )
    exposure.stressor.append(
        StressorChemical(
            chemical_id=retinoic_acid,
            concentration=QuantityValue(unit="µM", numeric_value="0.1"),
        )
    )

    obs = PhenotypeObservationSet()
    exposure.phenotype_observation.append(obs)
    obs.phenotype.append(
        Phenotype(
            stage="ZFS:0000044",
            severity="moderate",
            phenotype_term_id=head_abnormal,
            prevalence=QuantityValue(unit="%", numeric_value="48"),
        )
    )

    return study


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


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
        "PMID:40359302": _build_nishi_bpa_ra_study,
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
