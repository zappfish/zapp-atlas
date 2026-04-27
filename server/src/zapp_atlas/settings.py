from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = PACKAGE_DIR / "db" / "data"
DEFAULT_DB_PATH = DEFAULT_DATA_DIR / "zapp.db"
DEFAULT_UPLOAD_DIR = DEFAULT_DATA_DIR / "uploads"
DEFAULT_MAX_UPLOAD_BYTES = 50 * 1024 * 1024
DEFAULT_ORCID_BASE_URL = "https://orcid.org"
DEFAULT_ORCID_REDIRECT_URI = "http://127.0.0.1:8000/registered"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ZAPP_",
        env_ignore_empty=True,
        extra="ignore",
        str_strip_whitespace=True,
    )

    db_path: Path = DEFAULT_DB_PATH
    upload_dir: Path = DEFAULT_UPLOAD_DIR
    max_upload_bytes: int = DEFAULT_MAX_UPLOAD_BYTES
    skip_seed: bool = False

    aws_endpoint_url_s3: str | None = None
    bucket_name: str | None = None
    bucket_public_url_prefix: str | None = None

    orcid_client_id: str = ""
    orcid_client_secret: str = ""
    orcid_redirect_uri: str = DEFAULT_ORCID_REDIRECT_URI
    orcid_base_url: str = DEFAULT_ORCID_BASE_URL


def load_settings(**overrides) -> AppSettings:
    return AppSettings(**overrides)
