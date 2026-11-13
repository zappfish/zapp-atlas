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
definition of what counts as one, shared with the study service. It may also
carry a ``manufacturer`` (#175) — part of the cabinet grain, so the same
chemical from two suppliers is two entries — and a ``vehicle_type`` default.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    StringConstraints,
    field_validator,
)

from zapp_atlas.schema.pydantic_crud import (
    ManufacturerEnum,
    ResearchGroupRoleEnum,
    VehicleEnum,
)

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

# Free text that collapses blank to absent, so a rule requiring it (the
# ``other_not_listed`` escape hatches) cannot be satisfied with whitespace.
FreeText = Annotated[str | None, BeforeValidator(blank_to_none)]


class CabinetEntryIn(BaseModel):
    """Add a chemical to a group's cabinet. ``research_group`` is path-derived."""

    chemical_id: str
    nickname: Nickname = None
    manufacturer: ManufacturerEnum | None = None
    unrecognized_manufacturer_name: FreeText = None
    vehicle_type: VehicleEnum | None = None


class CabinetEntryPatch(BaseModel):
    """``None`` leaves a field as it is, so a nickname can be set or changed here
    but not removed."""

    chemical_id: str | None = None
    nickname: Nickname = None
    manufacturer: ManufacturerEnum | None = None
    unrecognized_manufacturer_name: FreeText = None
    vehicle_type: VehicleEnum | None = None


class CabinetEntryOut(_FromAttributes):
    id: int
    chemical_id: str
    nickname: str | None
    manufacturer: ManufacturerEnum | None
    unrecognized_manufacturer_name: str | None
    vehicle_type: VehicleEnum | None
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


# --- ZFIN reference lookups (/api/zfin) -------------------------------------
#
# Read models over ``zapp_atlas.zfin``'s dataclasses. Ids are CURIEs
# (``ZFIN:ZDB-ALT-...``). Vocabulary is ZFIN's own -- ``so_id`` for the kind
# of alteration, its zygosity words, reagent kinds by id prefix -- so the
# lookup surface stays put while the fish data model is reworked.


class ZfinGeneOut(_FromAttributes):
    gene_id: str
    symbol: str


class ZfinConstructOut(_FromAttributes):
    construct_id: str
    name: str


class ZfinWildtypeOut(_FromAttributes):
    fish_id: str
    genotype_id: str
    name: str
    abbreviation: str


class ZfinBackgroundOut(_FromAttributes):
    background_id: str  # a wild-type genotype
    name: str


class ZfinAlleleOut(_FromAttributes):
    allele_id: str
    symbol: str
    name: str  # differs from the symbol for deficiencies and translocations
    so_id: str | None  # the Sequence Ontology term for the kind of alteration
    type_label: str  # ZFIN's words for it
    mutagen: str | None
    is_transgenic: bool
    genes: list[ZfinGeneOut]  # usually one; none for most transgenics
    constructs: list[ZfinConstructOut]  # usually one; more for co-injected lines


class ZfinAlleleSearchOut(BaseModel):
    query: str
    total_matches: int
    results: list[ZfinAlleleOut]


class ZfinGenotypeAlleleOut(_FromAttributes):
    allele_id: str
    symbol: str
    zygosity: str  # unknown | heterozygous | homozygous | complex
    # The parents' zygosity, also "wild type"; None when ZFIN's unique name
    # did not parse.
    mother_zygosity: str | None
    father_zygosity: str | None


class ZfinGenotypeRefOut(_FromAttributes):
    genotype_id: str
    name: str  # as ZFIN writes it, alleles in <sup>
    name_plain: str


class ZfinGenotypeOut(ZfinGenotypeRefOut):
    unique_name: str | None  # ZFIN's zygosity-encoded handle; None for wild types
    alleles: list[ZfinGenotypeAlleleOut]
    backgrounds: list[ZfinBackgroundOut]


class ZfinReagentOut(_FromAttributes):
    reagent_id: str
    symbol: str
    kind: str  # morpholino | crispr | talen
    genes: list[ZfinGeneOut]


class ZfinFishOut(_FromAttributes):
    fish_id: str
    name: str
    name_plain: str
    genotype: ZfinGenotypeRefOut
    backgrounds: list[ZfinBackgroundOut]
    reagents: list[ZfinReagentOut]


class ZfinFishRefOut(_FromAttributes):
    fish_id: str
    name: str
    name_plain: str


class ZfinDescribedAlleleIn(BaseModel):
    allele_id: str
    # ZFIN's words. "unknown" matches only genotypes ZFIN records as unknown.
    zygosity: Literal["unknown", "heterozygous", "homozygous", "complex"]

    @field_validator("allele_id")
    @classmethod
    def _valid_allele(cls, value: str) -> str:
        if not _ZFIN_RE.match(value):
            raise ValueError(f"Invalid ZFIN allele id: {value}")
        return value


class ZfinResolveIn(BaseModel):
    """A fish as the curator describes it. Field names follow the fish data
    model so a draft can be sent as-is."""

    background_id: str | None = None  # a wild-type genotype id
    alleles: list[ZfinDescribedAlleleIn] = []
    reagents: list[str] = []  # transient reagent ids injected into the fish

    @field_validator("background_id")
    @classmethod
    def _valid_background(cls, value: str | None) -> str | None:
        if value is not None and not _ZFIN_RE.match(value):
            raise ValueError(f"Invalid ZFIN genotype id: {value}")
        return value

    @field_validator("reagents")
    @classmethod
    def _valid_reagents(cls, value: list[str]) -> list[str]:
        for reagent_id in value:
            if not _ZFIN_RE.match(reagent_id):
                raise ValueError(f"Invalid ZFIN reagent id: {reagent_id}")
        return value

    @field_validator("alleles")
    @classmethod
    def _one_zygosity_per_allele(cls, value: list[ZfinDescribedAlleleIn]) -> list:
        ids = [a.allele_id for a in value]
        if len(set(ids)) != len(ids):
            raise ValueError("An allele may be listed once")
        return value


class ZfinResolveCandidateOut(_FromAttributes):
    genotype: ZfinGenotypeRefOut
    backgrounds: list[ZfinBackgroundOut]  # as ZFIN recorded them; often none
    fish: list[ZfinFishRefOut]  # of this genotype, carrying exactly the described reagents


class ZfinResolveOut(_FromAttributes):
    """``genotype`` is set when exactly one registered genotype matches the
    description, and ``fish`` when exactly one fish of it carries the
    described reagents; ``candidates`` lists every genotype that matched, so
    an ambiguous description can be shown for what it is."""

    genotype: ZfinGenotypeRefOut | None
    fish: ZfinFishRefOut | None
    candidates: list[ZfinResolveCandidateOut]


class ZfinStatusOut(BaseModel):
    zfin_date: str  # the archive snapshot the bundle was built from
    counts: dict[str, int]
