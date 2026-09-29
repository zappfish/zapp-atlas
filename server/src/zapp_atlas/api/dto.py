"""Hand-written request/response models for the group-scoped API.

The generated ``pydantic_crud`` classes match the *data model*, not this API
boundary: they carry ``research_group`` (which these nested routes take from
the path), their Read side can't see the ``created_at``/``updated_at`` columns
that ``schema.constraints`` injects after generation, and their ``member``
field is CURIE-only. These DTOs are shaped for the endpoints instead —
path-derived ``research_group`` is never accepted in a body, and responses
expose the audit timestamps. ``ResearchGroup`` itself reuses the generated
``ResearchGroupCreate``/``ResearchGroupRead`` (they fit as-is).

A cabinet or tank entry may carry a ``nickname`` (#113): what the group calls
the chemical or line, and what it is listed under when picked. ``Nickname`` is
the one definition of what counts as one, shared with the study service. The
#114 fields (``manufacturer``/``vehicle``) live on the generated exposure
models.
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

from zapp_atlas.schema.pydantic_crud import (
    FishCreate,
    FishRead,
    ReagentTypeEnum,
    ResearchGroupRoleEnum,
    SequenceAlterationTypeEnum,
)

# Accepts a bare ORCID or an ``ORCID:`` CURIE; the service normalizes to CURIE.
_ORCID_RE = re.compile(r"^(ORCID:)?[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$")


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


def blank_to_none(value: object) -> object:
    """Trim a piece of text; text that is blank is no text at all."""
    if isinstance(value, str):
        return value.strip() or None
    return value


# A group's own name for something it works with. Optional wherever it appears,
# and unique within the group when given. The length limit matches the
# ``nickname`` slot's pattern in the schema, which is what the generated models
# and the client enforce; a test holds the two together.
Nickname = Annotated[
    Annotated[str, StringConstraints(max_length=200)] | None,
    BeforeValidator(blank_to_none),
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


class TankEntryIn(BaseModel):
    """Add a fish line to a group's tank. ``research_group`` is path-derived.

    ``nickname`` is what the group calls the line. It is optional: when given
    it is what the picker shows, and it is unique within the group; without
    one the picker falls back to the line's ZFIN details. A blank nickname is
    no nickname. ``fish`` is the generated create model — the same full Fish
    graph an experiment takes — so a line saved to the tank can later pre-fill
    a submission without losing detail. Its ZFIN-id patterns reject malformed
    identifiers with a 422.
    """

    nickname: Nickname = None
    fish: FishCreate


class TankEntryOut(_FromAttributes):
    id: int
    nickname: str | None
    fish: FishRead
    created_at: datetime | None
    updated_at: datetime | None


class ZfinAffectedGeneOut(_FromAttributes):
    gene_symbol: str
    gene_id: str


class ZfinConstructOut(_FromAttributes):
    construct_id: str
    construct_name: str


class ZfinAlleleOut(_FromAttributes):
    """One allele from the ZFIN reference index, shaped so a hit can pre-fill
    a MutantAllele/TransgenicAllele form card directly (same field names,
    CURIE-form ids that satisfy the generated models' patterns).

    ``constructs`` is a list because a co-injected transgenic line is one
    insertion event carrying several constructs (e.g. gz13Tg); the model's
    scalar construct slots take the first, the form can display them all.
    """

    allele_symbol: str
    allele_id: str
    is_transgenic: bool
    alteration_type: SequenceAlterationTypeEnum | None
    alteration_label: str
    mutagen: str | None
    # Institution registered for the symbol's naming prefix. Deliberately not
    # called "lab": ZFIN's per-feature Lab of Origin is curated separately
    # (and can differ, e.g. cross-institution collaborations) — it is only on
    # the ZFIN record page, which the UI links to.
    institution: str | None
    constructs: list[ZfinConstructOut]
    affected_genes: list[ZfinAffectedGeneOut]


class ZfinAlleleSearchOut(BaseModel):
    query: str
    total_matches: int
    indexed_alleles: int
    results: list[ZfinAlleleOut]


class ZfinReagentOut(_FromAttributes):
    """One transient reagent from the ZFIN reference index, shaped to pre-fill
    a TransientReagent form card (same field names, CURIE-form ids). The
    model's scalar gene slots take the first target; a few reagents hit
    several paralogs, which the form can display."""

    reagent_symbol: str
    reagent_id: str
    reagent_type: ReagentTypeEnum
    targeted_genes: list[ZfinAffectedGeneOut]


class ZfinReagentSearchOut(BaseModel):
    query: str
    total_matches: int
    indexed_reagents: int
    results: list[ZfinReagentOut]


class ZfinWildtypeOut(_FromAttributes):
    name: str
    abbreviation: str
    fish_id: str
    genotype_id: str
