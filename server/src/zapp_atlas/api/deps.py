"""FastAPI dependencies (database sessions, etc.)."""

from __future__ import annotations

from collections.abc import Generator

from fastapi import Request
from sqlalchemy.orm import Session

from zapp_atlas.db import get_engine, get_session_factory
from zapp_atlas.settings import AppSettings, load_settings


def _get_session_factory(request: Request):
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is None:
        settings = get_app_settings(request)
        engine = get_engine(settings=settings)
        session_factory = get_session_factory(engine)
        request.app.state.engine = engine
        request.app.state.session_factory = session_factory
    return session_factory


def get_session(request: Request) -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session and ensure it is closed."""

    session: Session = _get_session_factory(request)()
    try:
        yield session
    finally:
        session.close()


def get_app_settings(request: Request) -> AppSettings:
    settings = getattr(request.app.state, "settings", None)
    if settings is None:
        settings = load_settings()
        request.app.state.settings = settings
    return settings
