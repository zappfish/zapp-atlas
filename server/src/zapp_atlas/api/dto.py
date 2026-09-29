"""Hand-written request/response models for the group-scoped API.

The generated ``pydantic_crud`` classes match the *data model*, not this API
boundary: they carry ``research_group`` (which these nested routes take from
the path), their Read side can't see the ``created_at``/``updated_at`` columns
that ``schema.constraints`` injects after generation, and their ``member``
field is CURIE-only. These DTOs are shaped for the endpoints instead —
path-derived ``research_group`` is never accepted in a body, and responses
expose the audit timestamps. ``ResearchGroup`` itself reuses the generated
``ResearchGroupCreate``/``ResearchGroupRead`` (they fit as-is).

A cabinet entry may carry a ``nickname`` (#113): what the group calls the
chemical, and what it is listed under when picked. ``Nickname`` is the one
definition of what counts as one, shared with the study service. Fields for
#114 (``manufacturer``/``vehicle``) are intentionally absent; the shapes leave
room to add them later.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    StringConstraints,
    field_validator,
)

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


def clean_nickname(value: object) -> object:
    """Trim a nickname; one that is blank is no nickname at all."""
    if isinstance(value, str):
        return value.strip() or None
    return value


# A group's own name for something it works with. Optional wherever it appears,
# and unique within the group when given.
Nickname = Annotated[
    Annotated[str, StringConstraints(max_length=200)] | None,
    BeforeValidator(clean_nickname),
]


class CabinetEntryIn(BaseModel):
    """Add a chemical to a group's cabinet. ``research_group`` is path-derived."""

    chemical_id: str
    nickname: Nickname = None


class CabinetEntryPatch(BaseModel):
    """``None`` leaves a field as it is, so a nickname can be set or changed here
    but not removed."""

    chemical_id: str | None = None
    nickname: Nickname = None


class CabinetEntryOut(_FromAttributes):
    id: int
    chemical_id: str
    nickname: str | None
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
