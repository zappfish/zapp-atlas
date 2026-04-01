import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..schema.sqla import Base

SERVER_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = SERVER_DIR / "data" / "zapp.db"


def get_db_path() -> Path:
    env = os.getenv("ZAPP_DB_PATH")
    return Path(env).resolve() if env else DEFAULT_DB_PATH


def get_engine(db_path: Path | None = None):
    path = db_path or get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{path}", echo=False)


def get_session_factory(engine=None):
    engine = engine or get_engine()
    return sessionmaker(bind=engine)


def init_db(engine=None):
    engine = engine or get_engine()
    Base.metadata.create_all(engine)
    return engine
