"""The history of each study: a snapshot of the whole tree on every save.

Application state rather than part of the data model, so it is written by hand
here and not declared in the LinkML schema.
"""

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from zapp_atlas.schema.sqla import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class StudyRevision(Base):
    """A study as it stood after one save, and who made it."""

    __tablename__ = "StudyRevision"
    __table_args__ = (UniqueConstraint("study_id", "version"),)

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    study_id: Mapped[int] = mapped_column(Integer(), ForeignKey("Study.id"), index=True)
    # Counts up from 1 within a study.
    version: Mapped[int] = mapped_column(Integer())
    # The study and everything beneath it, as the API returned it at the time.
    # Never rewritten: a snapshot keeps the shape of the schema it was saved under.
    document: Mapped[dict] = mapped_column(JSON())
    saved_by: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
