from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Text, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from zapp_atlas.schema._gen.sqla import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class OrcidIdentity(Base):
    """Stored ORCID identity for an authenticated researcher."""

    __tablename__ = "OrcidIdentity"

    id: Mapped[str] = mapped_column(
        Text(), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    orcid_id: Mapped[str] = mapped_column(Text(), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

class ResearchGroup(Base):
    """ A named collection of users that have shared editing access """
    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text())

class ResearchGroupMember(Base):
    """ A join class between users and research groups that specifies the relationship permissions """
    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    user: Mapped[str] = relationship(foreign_keys="[OrcidIdentity.id]")
    role: Mapped[str] = mapped_column(Enum('admin','member'))
    group: Mapped[int] = relationship(foreign_keys=['ResearchGroup.id'])
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
