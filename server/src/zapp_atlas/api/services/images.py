"""Image persistence + blob-storage glue."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from zapp_atlas.db.image_storage import Storage, max_upload_bytes

from zapp_atlas.schema.sqla import (  # type: ignore
    Image,
    PhenotypeObservationSet,
)


class ImageTooLargeError(ValueError):
    pass


class UnsupportedImageTypeError(ValueError):
    pass


def _storage_key(image_id: int) -> str:
    return f"images/{image_id}"


def create_image_for_observation(
    session: Session,
    *,
    observation_id: int,
    data: bytes,
    content_type: str,
    storage: Storage,
    magnification: str | None = None,
    resolution: str | None = None,
    scale_bar: str | None = None,
    max_bytes: int | None = None,
) -> Optional[Image]:
    if not content_type.startswith("image/"):
        raise UnsupportedImageTypeError(content_type)

    limit = max_bytes if max_bytes is not None else max_upload_bytes()
    if len(data) > limit:
        raise ImageTooLargeError(f"{len(data)} > {limit}")

    obs = session.get(PhenotypeObservationSet, observation_id)
    if obs is None:
        return None

    image = Image(
        magnification=magnification,
        resolution=resolution,
        scale_bar=scale_bar,
    )
    obs.image.append(image)
    session.add(obs)
    session.commit()
    session.refresh(image)

    storage.put(_storage_key(image.id), data, content_type)
    return image


def get_image_by_id(session: Session, image_id: int) -> Optional[Image]:
    return session.get(Image, image_id)


def load_image_bytes(image_id: int, storage: Storage):
    return storage.get(_storage_key(image_id))


def image_url(image_id: int, storage: Storage) -> str | None:
    return storage.url_for(_storage_key(image_id))


def delete_image_row(session: Session, image, *, storage: Storage) -> None:
    """Delete an Image ORM row and its stored blob. Caller commits."""
    storage.delete(_storage_key(image.id))
    session.delete(image)


def delete_image(session: Session, image_id: int, *, storage: Storage) -> bool:
    image = get_image_by_id(session, image_id)
    if image is None:
        return False
    delete_image_row(session, image, storage=storage)
    session.commit()
    return True
