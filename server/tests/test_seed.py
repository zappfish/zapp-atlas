from __future__ import annotations

"""Tests for the dev seed script."""

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from zapp_atlas.db import init_db
from zapp_atlas.seed import seed


def _session_factory():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    init_db(engine)
    return sessionmaker(bind=engine)


def test_seed_creates_studies_with_full_graph() -> None:
    from zebrafish_toxicology_atlas_schema.datamodel.sqla import (
        ExposureEvent,
        Experiment,
        Phenotype,
        Study,
    )

    Session = _session_factory()
    session = Session()
    seed(session)

    assert session.query(func.count(Study.id)).scalar() >= 1
    assert session.query(func.count(Experiment.id)).scalar() >= 1
    assert session.query(func.count(ExposureEvent.id)).scalar() >= 1
    assert session.query(func.count(Phenotype.id)).scalar() >= 1

    study = session.query(Study).first()
    assert study is not None
    assert study.publication
    assert study.experiment  # relationship collection populated
    session.close()


def test_seed_is_idempotent() -> None:
    from zebrafish_toxicology_atlas_schema.datamodel.sqla import Study

    Session = _session_factory()
    session = Session()

    seed(session)
    first = session.query(func.count(Study.id)).scalar()

    seed(session)
    second = session.query(func.count(Study.id)).scalar()

    assert first == second
    session.close()
