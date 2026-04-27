from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from zapp_atlas.settings import AppSettings, DEFAULT_DB_PATH, load_settings
from zapp_atlas.schema.sqla import Base
import zapp_atlas.auth.models  # noqa: F401


def get_db_path(settings: AppSettings | None = None) -> Path:
    return (settings or load_settings()).db_path


def get_engine(db_path: Path | None = None, settings: AppSettings | None = None):
    path = db_path or get_db_path(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{path}", echo=False)


def get_session_factory(engine=None):
    engine = engine or get_engine()
    return sessionmaker(bind=engine)


def init_db(engine=None):
    engine = engine or get_engine()
    Base.metadata.create_all(engine)
    return engine
