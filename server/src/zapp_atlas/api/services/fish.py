"""Mapping from generated Fish payloads to the ORM graph.

Shared by the study/experiment services (the fish subject of an experiment) and
the fish-tank service (a group's saved lines). A Fish is built fresh per use
rather than upserted: two submissions naming the same line may still differ in
zygosity or parental details, so nothing short of the whole graph is a safe
natural key.
"""

from __future__ import annotations

from zapp_atlas.schema.pydantic_crud import (
    FishCreate,
    GenotypeCreate,
    MutantAlleleCreate,
    TransgenicAlleleCreate,
)
from zapp_atlas.schema.sqla import (  # type: ignore
    Fish,
    Genotype,
    MutantAllele,
    TransgenicAllele,
)


def _mutant_allele_from_create(payload: MutantAlleleCreate) -> MutantAllele:
    return MutantAllele(
        allele_id=payload.allele_id,
        allele_symbol=payload.allele_symbol,
        alteration_type=payload.alteration_type,
        affected_gene_id=payload.affected_gene_id,
        affected_gene_symbol=payload.affected_gene_symbol,
        zygosity=payload.zygosity,
        mother_zygosity=payload.mother_zygosity,
        father_zygosity=payload.father_zygosity,
    )


def _transgenic_allele_from_create(payload: TransgenicAlleleCreate) -> TransgenicAllele:
    return TransgenicAllele(
        allele_id=payload.allele_id,
        allele_symbol=payload.allele_symbol,
        construct_id=payload.construct_id,
        construct_name=payload.construct_name,
        alteration_type=payload.alteration_type,
        # The construct's driver / reporter gene — lets the atlas be searched by
        # gene across mutant and transgenic alleles alike.
        affected_gene_id=payload.affected_gene_id,
        affected_gene_symbol=payload.affected_gene_symbol,
        zygosity=payload.zygosity,
        mother_zygosity=payload.mother_zygosity,
        father_zygosity=payload.father_zygosity,
    )


def genotype_from_create(payload: GenotypeCreate | None) -> Genotype | None:
    """Map a GenotypeCreate to the ORM.

    Recursive: ``background`` is itself a Genotype (a wild-type strain such as
    AB is just a line with no alterations), so this calls back into itself
    rather than into a distinct background mapper. Recursion terminates when
    ``background`` is absent, which it is for a wild-type strain.
    """
    if payload is None:
        return None
    genotype = Genotype(
        genotype_zfin_id=payload.genotype_zfin_id,
        genotype_name=payload.genotype_name,
        background=genotype_from_create(payload.background),
    )
    for mutant in payload.mutant_allele or []:
        genotype.mutant_allele.append(_mutant_allele_from_create(mutant))
    for transgenic in payload.transgenic_allele or []:
        genotype.transgenic_allele.append(_transgenic_allele_from_create(transgenic))
    return genotype


def fish_from_create(payload: FishCreate | None) -> Fish | None:
    if payload is None:
        return None
    return Fish(
        name=payload.name,
        fish_zfin_id=payload.fish_zfin_id,
        genotype=genotype_from_create(payload.genotype),
    )
