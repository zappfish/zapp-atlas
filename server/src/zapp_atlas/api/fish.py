"""The ZFIN ids of a described fish.

``fish_zfin_id`` and ``genotype_zfin_id`` say which of ZFIN's registered
records a description matches. They follow from the description, so the
server works them out each time a fish is stored and a request cannot set
them. Unlike the rest of ``api`` this names slots, since the matching is
about these ones in particular.
"""

from sqlalchemy.orm import Session

from zapp_atlas.schema.sqla import Fish
from zapp_atlas.zfin import Resolution, Zfin


def set_zfin_ids(session: Session, fish: Fish) -> None:
    found = _registered(session.info["zfin"], fish)
    fish.genotype_zfin_id = found.genotype.genotype_id if found.genotype else None
    fish.fish_zfin_id = found.fish.fish_id if found.fish else None


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
