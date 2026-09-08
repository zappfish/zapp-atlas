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


class TankEntryIn(BaseModel):
    """Add a fish line to a group's tank. ``research_group`` is path-derived.

    ``fish`` is the generated create model — the same full Fish graph
    an experiment takes — so a line saved to the tank can later pre-fill a
    submission without losing detail. Its ZFIN-id patterns reject malformed
    identifiers with a 422.
    """

    fish: FishCreate


class TankEntryOut(_FromAttributes):
    id: int
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
