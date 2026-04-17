from sqlalchemy import create_engine, inspect, text

from server.db import init_db, get_session_factory
from zebrafish_toxicology_atlas_schema.datamodel.sqla import (
    ChemicalEntity,
    Experiment,
    ExposureEvent,
    Fish,
    Phenotype,
    PhenotypeObservationSet,
    PhenotypeTerm,
    QuantityValue,
    StressorChemical,
    Study,
)


def test_init_db_creates_expected_tables():
    engine = create_engine("sqlite:///:memory:")
    init_db(engine)

    tables = set(inspect(engine).get_table_names())
    expected = {
        "Study",
        "Experiment",
        "ExposureEvent",
        "Phenotype",
        "PhenotypeObservationSet",
        "Control",
        "Fish",
        "ChemicalEntity",
        "PhenotypeTerm",
        "QuantityValue",
        "Image",
        "ControlImage",
        "StressorChemical",
        "Regimen",
    }
    missing = expected - tables
    assert not missing, f"Missing tables: {missing}"


def test_session_factory_connects():
    engine = create_engine("sqlite:///:memory:")
    init_db(engine)
    Session = get_session_factory(engine)
    session = Session()
    result = session.execute(text("SELECT 1"))
    assert result.scalar() == 1
    session.close()


def test_study_round_trip():
    """
    Persist a realistic study based on Lam et al. 2011 (PMID 22194820) —
    BPA early-life exposure toxicity in zebrafish — then read everything
    back and verify the object graph survived the round trip.
    """
    engine = create_engine("sqlite:///:memory:")
    init_db(engine)
    Session = get_session_factory(engine)
    session = Session()

    # --- leaf / reference entities ----------------------------------------

    fish = Fish(zfin_id="ZDB-GENO-960809-7", name="AB")

    bpa = ChemicalEntity(
        uri="http://purl.obolibrary.org/obo/CHEBI_33216",
        chebi_id="CHEBI:33216",
        cas_id="80-05-7",
        chemical_name="bisphenol A",
    )

    concentration = QuantityValue(unit="µg/L", numeric_value="100")

    zp_pericardial_edema = PhenotypeTerm(
        term_uri="ZP:0105827",
        term_label="pericardial region edematous, abnormal",
    )
    zp_craniofacial = PhenotypeTerm(
        term_uri="ZP:0001609",
        term_label="head morphology, abnormal",
    )

    # --- study / experiment -----------------------------------------------

    study = Study(
        publication="PMID:22194820",
        lab="Gong Lab, National University of Singapore",
        annotator=["Lam SH", "Gong Z"],
    )

    experiment = Experiment(
        standard_rearing_condition=True,
        fish=fish,
    )
    study.experiment.append(experiment)

    # --- exposure event with stressor chemical ----------------------------

    exposure = ExposureEvent(
        exposure_start_stage="ZFS:0000011",  # Blastula:1k-cell (~3 hpf)
        exposure_end_stage="ZFS:0000039",    # Larval:Days 7-13 (~7 dpf)
    )
    experiment.exposure_event.append(exposure)

    stressor = StressorChemical(
        chemical_id=bpa,
        concentration=concentration,
        manufacturer="Sigma-Aldrich",
    )
    exposure.stressor.append(stressor)

    # --- phenotype observations -------------------------------------------

    obs_set = PhenotypeObservationSet()
    exposure.phenotype_observation.append(obs_set)

    pheno_edema = Phenotype(
        stage="ZFS:0000035",  # Larval:Protruding-mouth (~72 hpf)
        severity="moderate",
        phenotype_term_id=zp_pericardial_edema,
    )
    pheno_craniofacial = Phenotype(
        stage="ZFS:0000035",  # Larval:Protruding-mouth (~72 hpf)
        severity="mild",
        phenotype_term_id=zp_craniofacial,
    )
    obs_set.phenotype.extend([pheno_edema, pheno_craniofacial])

    # --- persist ----------------------------------------------------------

    session.add(study)
    session.commit()

    # --- query back and verify --------------------------------------------

    loaded_study = session.query(Study).one()
    assert loaded_study.publication == "PMID:22194820"
    assert loaded_study.lab == "Gong Lab, National University of Singapore"
    assert set(loaded_study.annotator) == {"Lam SH", "Gong Z"}

    [loaded_exp] = loaded_study.experiment
    assert loaded_exp.standard_rearing_condition is True
    assert loaded_exp.fish.zfin_id == "ZDB-GENO-960809-7"
    assert loaded_exp.fish.name == "AB"

    [loaded_ee] = loaded_exp.exposure_event
    assert loaded_ee.exposure_start_stage == "ZFS:0000011"
    assert loaded_ee.exposure_end_stage == "ZFS:0000039"

    [loaded_stressor] = loaded_ee.stressor
    assert loaded_stressor.chemical_id.chemical_name == "bisphenol A"
    assert loaded_stressor.chemical_id.chebi_id == "CHEBI:33216"
    assert loaded_stressor.chemical_id.cas_id == "80-05-7"
    assert loaded_stressor.concentration.numeric_value == "100"
    assert loaded_stressor.concentration.unit == "µg/L"
    assert loaded_stressor.manufacturer == "Sigma-Aldrich"

    [loaded_obs] = loaded_ee.phenotype_observation
    phenotypes = sorted(
        loaded_obs.phenotype, key=lambda p: p.phenotype_term_id.term_label
    )
    assert len(phenotypes) == 2

    assert phenotypes[0].phenotype_term_id.term_label == "head morphology, abnormal"
    assert phenotypes[0].phenotype_term_id.term_uri == "ZP:0001609"
    assert phenotypes[0].severity == "mild"
    assert phenotypes[0].stage == "ZFS:0000035"

    assert phenotypes[1].phenotype_term_id.term_label == "pericardial region edematous, abnormal"
    assert phenotypes[1].phenotype_term_id.term_uri == "ZP:0105827"
    assert phenotypes[1].severity == "moderate"
    assert phenotypes[1].stage == "ZFS:0000035"

    session.close()
