from sqlalchemy import create_engine, inspect, text

from db import init_db, get_session_factory


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
