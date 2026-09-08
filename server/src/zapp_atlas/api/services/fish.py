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
    MutantAlleleCreate,
    TransgenicAlleleCreate,
    TransientReagentCreate,
)
from zapp_atlas.schema.sqla import (  # type: ignore
    Fish,
    MutantAllele,
    TransgenicAllele,
    TransientReagent,
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


def _transient_reagent_from_create(payload: TransientReagentCreate) -> TransientReagent:
    return TransientReagent(
        reagent_id=payload.reagent_id,
        reagent_symbol=payload.reagent_symbol,
        reagent_type=payload.reagent_type,
        affected_gene_id=payload.affected_gene_id,
        affected_gene_symbol=payload.affected_gene_symbol,
    )


def fish_from_create(payload: FishCreate | None) -> Fish | None:
    if payload is None:
        return None
    fish = Fish(
        name=payload.name,
        fish_zfin_id=payload.fish_zfin_id,
        genotype_zfin_id=payload.genotype_zfin_id,
        background_name=payload.background_name,
        background_zfin_id=payload.background_zfin_id,
    )
    for mutant in payload.mutant_allele or []:
        fish.mutant_allele.append(_mutant_allele_from_create(mutant))
    for transgenic in payload.transgenic_allele or []:
        fish.transgenic_allele.append(_transgenic_allele_from_create(transgenic))
    for reagent in payload.transient_reagent or []:
        fish.transient_reagent.append(_transient_reagent_from_create(reagent))
    return fish
