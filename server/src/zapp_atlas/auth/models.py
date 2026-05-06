from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from zapp_atlas.schema._gen.sqla import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class OrcidAuthToken(Base):
    """Stored ORCID identity for an authenticated researcher."""

    __tablename__ = "OrcidAuthToken"

    id: Mapped[str] = mapped_column(
        Text(), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    orcid_id: Mapped[str] = mapped_column(Text(), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
