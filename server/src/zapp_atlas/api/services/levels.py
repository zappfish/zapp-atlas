"""Creating, replacing and deleting a level of the study tree.

Every change is recorded: after it, the whole study is snapshotted as a new
revision, so a study's history can be read back however many separate saves
went into it.
"""

from contextlib import AbstractContextManager

from pydantic import BaseModel
from sqlalchemy import delete as delete_rows
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from zapp_atlas.api.authz import orcid_curie
from zapp_atlas.api.layout import layout
from zapp_atlas.api.persistence import conflicts_as_409
from zapp_atlas.api.tree import assign, build, images_within, study_of
from zapp_atlas.auth.models import OrcidIdentity
from zapp_atlas.db.image_storage import Storage
from zapp_atlas.db.revisions import StudyRevision
from zapp_atlas.schema.pydantic_crud import StudyRead
from zapp_atlas.schema.sqla import Base, Study

NICKNAME_TAKEN = "That nickname is already used by another study in this research group"


def image_key(image_id: int) -> str:
    """Where an image's file is kept."""
    return f"images/{image_id}"


def create(
    session: Session, level_name: str, body: BaseModel, *, parent: Base | None, by: OrcidIdentity
) -> Base:
    """Store a new row of a level, inside ``parent`` unless it is the outermost."""
    with _conflicts(session):
        row = build(session, level_name, body)
        if parent is None:
            session.add(row)
        else:
            getattr(parent, layout().levels[level_name].slot_in_parent).append(row)
        session.flush()
    _record(session, study_of(session, level_name, row), by)
    session.commit()
    return row


def replace(
    session: Session, level_name: str, row: Base, body: BaseModel, *, by: OrcidIdentity
) -> Base:
    """Make a stored row say what ``body`` says, leaving the next level alone."""
    with _conflicts(session):
        assign(session, level_name, row, body)
        session.flush()
    _record(session, study_of(session, level_name, row), by)
    session.commit()
    return row


def delete(
    session: Session, level_name: str, row: Base, storage: Storage, *, by: OrcidIdentity
) -> None:
    """Delete a row, everything beneath it, and the files of any images there."""
    keys = [image_key(image.id) for image in images_within(level_name, row)]
    study = study_of(session, level_name, row)
    session.delete(row)
    if row is study:
        session.execute(delete_rows(StudyRevision).where(StudyRevision.study_id == study.id))
    else:
        session.flush()
        # The rows just deleted are still in their parents' loaded collections.
        session.expire_all()
        _record(session, study, by)
    session.commit()
    for key in keys:
        storage.delete(key)


def _conflicts(session: Session) -> AbstractContextManager[None]:
    """Answer 409 for a unique key broken while a row is being stored.

    Wraps the assignment as well as the flush: SQLAlchemy may flush on its own
    partway through, when a relationship is loaded in order to be replaced.
    """
    return conflicts_as_409(
        session,
        "That conflicts with something that is already saved",
        named={"nickname": NICKNAME_TAKEN},
    )


def _record(session: Session, study: Study, by: OrcidIdentity) -> None:
    """Snapshot a study, as it now stands, as its next revision."""
    latest = session.scalar(
        select(func.max(StudyRevision.version)).where(StudyRevision.study_id == study.id)
    )
    session.add(
        StudyRevision(
            study_id=study.id,
            version=(latest or 0) + 1,
            document=StudyRead.model_validate(study).model_dump(mode="json"),
            saved_by=orcid_curie(by.orcid_id),
        )
    )
