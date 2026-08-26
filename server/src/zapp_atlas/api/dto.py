"""Hand-written request/response models for the group-scoped API.

The generated ``pydantic_crud`` classes match the *data model*, not this API
boundary: they carry ``research_group`` (which these nested routes take from
the path), their Read side can't see the ``created_at``/``updated_at`` columns
that ``schema.constraints`` injects after generation, and their ``member``
field is CURIE-only. These DTOs are shaped for the endpoints instead —
path-derived ``research_group`` is never accepted in a body, and responses
expose the audit timestamps. ``ResearchGroup`` itself reuses the generated
``ResearchGroupCreate``/``ResearchGroupRead`` (they fit as-is).

Fields for #113 (``nickname``) and #114 (``manufacturer``/``vehicle``) are
intentionally absent; the shapes leave room to add them later.
"""

from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from zapp_atlas.schema.pydantic_crud import ResearchGroupRoleEnum

# Accepts a bare ORCID or an ``ORCID:`` CURIE; the service normalizes to CURIE.
_ORCID_RE = re.compile(r"^(ORCID:)?[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$")
# ZFIN line identifier, matching the schema's ``zfin_id`` pattern.
_ZFIN_RE = re.compile(r"^ZFIN:ZDB-[A-Z]+-\d{6}-\d+$")


class _FromAttributes(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MemberIn(BaseModel):
    """Add a member to a group. ``research_group`` comes from the path."""

    member: str
    role: ResearchGroupRoleEnum

    @field_validator("member")
    @classmethod
    def _valid_orcid(cls, value: str) -> str:
        if not _ORCID_RE.match(value):
            raise ValueError(f"Invalid ORCID: {value}")
        return value


class MemberOut(_FromAttributes):
    id: int
    member: str
    role: ResearchGroupRoleEnum
    created_at: datetime | None
    updated_at: datetime | None


class CabinetEntryIn(BaseModel):
    """Add a chemical to a group's cabinet. ``research_group`` is path-derived."""

    chemical_id: str


class CabinetEntryPatch(BaseModel):
    chemical_id: str | None = None


class CabinetEntryOut(_FromAttributes):
    id: int
    chemical_id: str
    created_at: datetime | None
    updated_at: datetime | None


class FishRef(_FromAttributes):
    zfin_id: str
    name: str

    @field_validator("zfin_id")
    @classmethod
    def _valid_zfin(cls, value: str) -> str:
        if not _ZFIN_RE.match(value):
            raise ValueError(f"Invalid ZFIN id: {value}")
        return value


class TankEntryIn(BaseModel):
    """Add a fish line to a group's tank. ``research_group`` is path-derived."""

    fish: FishRef


class TankEntryOut(_FromAttributes):
    id: int
    fish: FishRef
    created_at: datetime | None
    updated_at: datetime | None
