"""FastAPI dependencies (database sessions, etc.)."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from server.db import get_engine, get_session_factory


# In production we may want more explicit lifecycle management, but for now
# having a module-level engine is fine.
_engine = get_engine()
_SessionLocal = get_session_factory(_engine)


def get_session() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session and ensure it is closed."""

    session: Session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()
