"""What ZFIN says of a described fish.

A fish is described by the ZFIN ids of what it is made of: its background,
its alleles with their genes and constructs, and any injected reagents. Each
of those ids has a name beside it. The server takes the names from ZFIN's
registry, so a request cannot give an id one name and mean another, and
refuses an id the registry does not have.

``fish_zfin_id`` and ``genotype_zfin_id`` say which of ZFIN's registered
records the whole description matches. They follow from the description, so
the server works them out each time a fish is stored and a request cannot set
them.

A part described without an id, an allele ZFIN has not registered, keeps the
name it was given, and makes no call on the registry.

Unlike the rest of ``api`` this names slots, since ZFIN's records are about
these ones in particular.
"""

from sqlalchemy.orm import Session

from zapp_atlas.api.errors import SchemaRuleViolation
from zapp_atlas.schema.sqla import Fish
from zapp_atlas.schema.view import value_for_meaning
from zapp_atlas.zfin import Resolution, Zfin


def describe_from_zfin(session: Session, fish: Fish) -> None:
    """Name the fish's parts as ZFIN does, then say which record it matches."""
    zfin: Zfin = session.info["zfin"]
    _name_parts(zfin, fish)
    found = _registered(zfin, fish)
    fish.genotype_zfin_id = found.genotype.genotype_id if found.genotype else None
    fish.fish_zfin_id = found.fish.fish_id if found.fish else None


def _known[Record](record: Record | None, zfin_id: str, kind: str) -> Record:
    if record is None:
        raise SchemaRuleViolation(f"{zfin_id} is not {kind} ZFIN has.")
    return record


def _name_parts(zfin: Zfin, fish: Fish) -> None:
    """Give each part named by a ZFIN id the name ZFIN has for it.

    Reading the registry is what answers 503 when it is not installed, so a
    fish that names no ids is stored without it.
    """
    if fish.background_zfin_id is not None:
        line = _known(
            zfin.wildtype(fish.background_zfin_id), fish.background_zfin_id, "a wild-type line"
        )
        fish.background_name = line.abbreviation

    for allele in fish.allele:
        if allele.allele_zfin_id is not None:
            known = _known(zfin.allele(allele.allele_zfin_id), allele.allele_zfin_id, "an allele")
            allele.allele_symbol = known.symbol
            allele.alteration_type = value_for_meaning("SequenceAlterationTypeEnum", known.so_id)
        if allele.construct_zfin_id is not None:
            allele.construct_name = _known(
                zfin.construct_name(allele.construct_zfin_id),
                allele.construct_zfin_id,
                "a construct",
            )

    for reagent in fish.transient_reagent:
        if reagent.reagent_zfin_id is not None:
            known = _known(
                zfin.reagent(reagent.reagent_zfin_id), reagent.reagent_zfin_id, "a reagent"
            )
            reagent.reagent_symbol = known.symbol
            reagent.reagent_type = known.kind

    for part in (*fish.allele, *fish.transient_reagent):
        if part.affected_gene_zfin_id is not None:
            part.affected_gene_symbol = _known(
                zfin.gene_symbol(part.affected_gene_zfin_id), part.affected_gene_zfin_id, "a gene"
            )


def _registered(zfin: Zfin, fish: Fish) -> Resolution:
    """What ZFIN has registered for the description.

    Nothing, without a bundle to ask. Nothing either when an allele or
    reagent has no ZFIN id, or an allele is listed twice: matching the rest
    of the description would name a fish that differs from this one.
    """
    alleles = {allele.allele_zfin_id: allele.zygosity for allele in fish.allele}
    reagents = {reagent.reagent_zfin_id for reagent in fish.transient_reagent}
    if not zfin.available or None in alleles or None in reagents or len(alleles) < len(fish.allele):
        return Resolution(())
    return zfin.resolve(alleles, fish.background_zfin_id, reagents)
