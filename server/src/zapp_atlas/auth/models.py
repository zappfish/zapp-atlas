from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from zapp_atlas.schema._gen.sqla import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class OrcidAuthToken(Base):
    """Stored ORCID OAuth token for an authenticated researcher."""

    __tablename__ = "OrcidAuthToken"

    id: Mapped[str] = mapped_column(
        Text(), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    orcid_id: Mapped[str] = mapped_column(Text(), index=True)
    name: Mapped[str | None] = mapped_column(Text())
    access_token: Mapped[str] = mapped_column(Text())
    refresh_token: Mapped[str | None] = mapped_column(Text())
    token_type: Mapped[str | None] = mapped_column(Text())
    scope: Mapped[str | None] = mapped_column(Text())
    expires_in: Mapped[int | None] = mapped_column(Integer())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

