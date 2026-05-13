from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from zapp_atlas.api.deps import get_session
from zapp_atlas.main import create_app
from zapp_atlas.settings import AppSettings


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

    app = create_app(AppSettings(skip_seed=True, upload_dir=tmp_path))

    def _override_get_session():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = _override_get_session
    return TestClient(app)
