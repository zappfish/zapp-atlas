"""Creating, replacing and deleting a level of the study tree."""

from contextlib import AbstractContextManager

from pydantic import BaseModel
from sqlalchemy.orm import Session

from zapp_atlas.api.layout import layout
from zapp_atlas.api.persistence import conflicts_as_409
from zapp_atlas.api.tree import assign, build, images_within
from zapp_atlas.db.image_storage import Storage
from zapp_atlas.schema.sqla import Base

NICKNAME_TAKEN = "That nickname is already used by another study in this research group"


def image_key(image_id: int) -> str:
    """Where an image's file is kept."""
    return f"images/{image_id}"


def _conflicts(session: Session) -> AbstractContextManager[None]:
    """Answer 409 for a unique key broken while a row is being stored.

    Wraps the assignment as well as the commit: SQLAlchemy may flush on its own
    partway through, when a relationship is loaded in order to be replaced.
    """
    return conflicts_as_409(
        session,
        "That conflicts with something that is already saved",
        named={"nickname": NICKNAME_TAKEN},
    )


def create(session: Session, level_name: str, body: BaseModel, *, parent: Base | None) -> Base:
    """Store a new row of a level, inside ``parent`` unless it is the outermost."""
    with _conflicts(session):
        row = build(session, level_name, body)
        if parent is None:
            session.add(row)
        else:
            getattr(parent, layout().levels[level_name].slot_in_parent).append(row)
        session.commit()
    return row


def replace(session: Session, level_name: str, row: Base, body: BaseModel) -> Base:
    """Make a stored row say what ``body`` says, leaving the next level alone."""
    with _conflicts(session):
        assign(session, level_name, row, body)
        session.commit()
    return row


def delete(session: Session, level_name: str, row: Base, storage: Storage) -> None:
    """Delete a row, everything beneath it, and the files of any images there."""
    keys = [image_key(image.id) for image in images_within(level_name, row)]
    session.delete(row)
    session.commit()
    for key in keys:
        storage.delete(key)
