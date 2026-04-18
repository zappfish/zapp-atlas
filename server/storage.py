"""Image storage abstraction.

Two backends:

* ``LocalFilesystemStorage`` — writes blobs under a local directory.
  Used when no S3-compatible bucket endpoint is configured.
* ``BucketStorage`` — any S3-compatible object store (Tigris, Cloudflare
  R2, MinIO, Backblaze B2, ...). Activated when ``AWS_ENDPOINT_URL_S3``
  and ``BUCKET_NAME`` are both set. Env var names follow the boto3 /
  AWS SDK convention so they match what ``fly storage create`` and most
  provider docs emit.

Callers get a ``Storage`` instance from ``get_storage()``; backends are
swapped without the caller noticing.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class StoredObject:
    """Bytes + their content type. Returned from ``Storage.get()``."""

    data: bytes
    content_type: str


class Storage(ABC):
    @abstractmethod
    def put(self, key: str, data: bytes, content_type: str) -> None: ...

    @abstractmethod
    def get(self, key: str) -> StoredObject | None: ...

    @abstractmethod
    def url_for(self, key: str) -> str | None:
        """Return a URL clients can fetch directly, or None to force streaming."""


class LocalFilesystemStorage(Storage):
    """Writes blobs under ``root``; companions a ``.type`` file per blob for
    content-type roundtrip."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.root / key

    def put(self, key: str, data: bytes, content_type: str) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.with_suffix(path.suffix + ".type").write_text(content_type)

    def get(self, key: str) -> StoredObject | None:
        path = self._path(key)
        if not path.is_file():
            return None
        type_path = path.with_suffix(path.suffix + ".type")
        content_type = (
            type_path.read_text().strip()
            if type_path.is_file()
            else "application/octet-stream"
        )
        return StoredObject(data=path.read_bytes(), content_type=content_type)

    def url_for(self, key: str) -> str | None:
        return None  # force streaming via the app


class BucketStorage(Storage):
    """S3-compatible object-store backend (Tigris, R2, MinIO, ...). Lazy-imports boto3."""

    def __init__(
        self, *, endpoint_url: str, bucket: str, public_url_prefix: str | None = None
    ) -> None:
        import boto3  # noqa: PLC0415 — lazy, optional

        self._bucket = bucket
        self._client = boto3.client("s3", endpoint_url=endpoint_url)
        self._public_url_prefix = public_url_prefix

    def put(self, key: str, data: bytes, content_type: str) -> None:
        self._client.put_object(
            Bucket=self._bucket, Key=key, Body=data, ContentType=content_type
        )

    def get(self, key: str) -> StoredObject | None:
        try:
            resp = self._client.get_object(Bucket=self._bucket, Key=key)
        except self._client.exceptions.NoSuchKey:
            return None
        return StoredObject(
            data=resp["Body"].read(),
            content_type=resp.get("ContentType", "application/octet-stream"),
        )

    def url_for(self, key: str) -> str | None:
        if self._public_url_prefix:
            return f"{self._public_url_prefix.rstrip('/')}/{key}"
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=3600,
        )


def _default_local_dir() -> Path:
    env = os.getenv("ZAPP_UPLOAD_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent / "data" / "uploads"


def get_storage() -> Storage:
    endpoint = os.getenv("AWS_ENDPOINT_URL_S3")
    bucket = os.getenv("BUCKET_NAME")
    if endpoint and bucket:
        return BucketStorage(
            endpoint_url=endpoint,
            bucket=bucket,
            public_url_prefix=os.getenv("ZAPP_BUCKET_PUBLIC_URL_PREFIX"),
        )
    return LocalFilesystemStorage(root=_default_local_dir())


def max_upload_bytes() -> int:
    raw = os.getenv("ZAPP_MAX_UPLOAD_BYTES")
    return int(raw) if raw else 50 * 1024 * 1024
