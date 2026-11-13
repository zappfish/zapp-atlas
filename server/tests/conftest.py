from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from zapp_atlas.api.deps import get_session
from zapp_atlas.main import create_app
from zapp_atlas.settings import AppSettings


@pytest.fixture(autouse=True)
def _no_orcid_public_api(monkeypatch) -> None:
    """Keep tests off the network: ORCID public-name lookups find nothing.

    Tests that care about the prefetched name monkeypatch the same symbol.
    """
    monkeypatch.setattr(
        "zapp_atlas.auth.services.fetch_orcid_public_name",
        lambda *args, **kwargs: None,
    )


@pytest.fixture
def client(tmp_path) -> TestClient:
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
    settings = AppSettings(skip_seed=True, upload_dir=tmp_path, _env_file=None)
    app = create_app(settings)

    def _override_get_session():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = _override_get_session
    # open_session (used outside routes, e.g. the templating context processor)
    # resolves through app.state.session_factory rather than get_session, so
    # point it at the same test database.
    app.state.session_factory = SessionLocal
    return TestClient(app)


@pytest.fixture(scope="session")
def zfin_db(tmp_path_factory) -> Path:
    """zfin.db built from tests/zfin_fixture by the real extdata builder."""
    import subprocess

    repo = Path(__file__).resolve().parents[2]
    output = tmp_path_factory.mktemp("zfin") / "zfin.db"
    subprocess.run(
        [
            "uv",
            "run",
            "--quiet",
            "--script",
            str(repo / "extdata" / "scripts" / "zfin_db.py"),
            str(output),
            str(Path(__file__).parent / "zfin_fixture"),
            "--zfin-date",
            "2026.11.01",
        ],
        check=True,
    )
    return output
