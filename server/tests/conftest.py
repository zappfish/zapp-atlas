from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from zapp_atlas.labels import Labels
from zapp_atlas.main import create_app
from zapp_atlas.settings import AppSettings
from zapp_atlas.zfin import Zfin


@pytest.fixture(autouse=True)
def _no_orcid_public_api(monkeypatch) -> None:
    """Keep tests off the network: ORCID public-name lookups find nothing.

    Tests that care about the prefetched name monkeypatch the same symbol.
    """
    monkeypatch.setattr(
        "zapp_atlas.auth.services.fetch_orcid_public_name",
        lambda *args, **kwargs: None,
    )


@pytest.fixture(scope="session")
def labels_db(tmp_path_factory) -> Path:
    """labels.db built from tests/labels_fixture: the few terms the tests
    name, and ZFIN's stages."""
    from support import LABELS_FIXTURES, built

    return built(
        "labels_db.py",
        tmp_path_factory.mktemp("labels") / "labels.db",
        *map(str, LABELS_FIXTURES),
    )


@pytest.fixture
def extdata_dir(tmp_path_factory, labels_db, zfin_db) -> Path:
    """Where the app looks for its reference bundle: a directory holding the
    tests' own term labels and ZFIN records and nothing else, whatever the
    developer has built. A module overrides this to have no bundle."""
    import shutil

    # Apart from the test's own directory, which is where uploads are kept.
    bundle = tmp_path_factory.mktemp("extdata")
    shutil.copy(labels_db, bundle / "labels.db")
    shutil.copy(zfin_db, bundle / "zfin.db")
    return bundle


@pytest.fixture
def client(tmp_path, extdata_dir) -> TestClient:
    from zapp_atlas.db import init_db

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    init_db(engine)
    SessionLocal = sessionmaker(bind=engine)

    # Build settings hermetically: `_env_file=None` stops pydantic-settings from
    # reading the developer's server/.env, so tests don't depend on local config.
    # In particular ZAPP_DEV_AUTH (which CLAUDE.md tells you to enable for UI work)
    # must not leak in, or test_dev_login_is_absent_by_default fails on your machine
    # while passing on CI.
    settings = AppSettings(
        skip_seed=True, upload_dir=tmp_path, extdata_dir=extdata_dir, _env_file=None
    )
    app = create_app(settings)
    # Every session the app opens, in a route or outside one, comes from here.
    app.state.session_factory = SessionLocal
    return TestClient(app)


@pytest.fixture(scope="session")
def zfin_db(tmp_path_factory) -> Path:
    """zfin.db built from tests/zfin_fixture by the real extdata builder."""
    from support import ZFIN_FIXTURE, built

    return built(
        "zfin_db.py",
        tmp_path_factory.mktemp("zfin") / "zfin.db",
        str(ZFIN_FIXTURE),
        "--zfin-date",
        "2026.11.01",
    )


@pytest.fixture
def session(labels_db, zfin_db) -> Iterator[Session]:
    """A session on an empty in-memory database, for tests below the HTTP layer."""
    from zapp_atlas.db import init_db

    engine = create_engine("sqlite:///:memory:", poolclass=StaticPool)
    init_db(engine)
    with Session(engine) as session:
        # As the app's sessions carry them.
        session.info["zfin"] = Zfin(zfin_db)
        session.info["labels"] = Labels(labels_db)
        yield session


@pytest.fixture
def group(client: TestClient) -> int:
    """A research group whose admin, the curator, is left signed in."""
    from support import CURATOR, make_group, signin

    signin(client, CURATOR)
    return make_group(client, "Test Lab")


@pytest.fixture
def tree(client: TestClient, group: int) -> dict[str, dict]:
    """One row of every JSON level, each inside the one before, as created."""
    from support import make_tree

    return make_tree(client, group)
