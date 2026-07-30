"""Placeholder data for the research group dashboard.

The group-scoped endpoints (research groups, fish tank, chemical cabinet,
submissions) are not wired into this page yet — see the API in #130. This
module supplies stand-in data shaped like those responses so the dashboard
can be built and reviewed; swap these calls for the real services when the
endpoints land, leaving the template unchanged.

Fish carry optional genotype detail (background, mutations, transgenes). The
API returns only ``zfin_id`` and ``name`` today; the extra fields are modelled
as optional so the template renders them per fish when present and stays clean
when absent.
"""

from __future__ import annotations


def _fish(zfin_id, name, *, background=None, mutations=(), transgenes=()):
    return {
        "zfin_id": zfin_id,
        "name": name,
        "background": background,
        "mutations": list(mutations),
        "transgenes": list(transgenes),
    }


# A mix of fully-annotated fish and bare name+id fish, to exercise the
# conditional genotype rendering.
FISH_TANK = [
    _fish(
        "ZFIN:ZDB-FISH-150901-27842",
        "snapc1bfh111/fh111; w200Tg (AB)",
        background="AB",
        mutations=[{"allele": "fh111", "zygosity": "homo", "gene": "snapc3b"}],
        transgenes=[
            {"allele": "w200Tg", "zygosity": "unknown", "construct": "Tg(mpeg1:YFP)"}
        ],
    ),
    _fish(
        "ZFIN:ZDB-FISH-150901-8850",
        "pax2a^th16/th16",
        background="AB",
        transgenes=[
            {"allele": "w200Tg", "zygosity": "unknown", "construct": "Tg(mpeg1:YFP)"}
        ],
    ),
    _fish("ZFIN:ZDB-FISH-150901-15216", "TU wild type"),
]

CABINET = [
    {"id": 1, "chemical_id": "CHEBI:16236"},
    {"id": 2, "chemical_id": "CHEBI:35456"},
    {"id": 3, "chemical_id": "CHEBI:39867"},
]

SUBMISSIONS = [
    {
        "title": "sox2 expression — 24 hpf neural tube",
        "status": "Published",
        "date": "2026-05-14",
    },
    {
        "title": "pax2a optic cup ISH dataset",
        "status": "In Progress",
        "date": "2026-06-01",
    },
]

RESEARCH_GROUPS = [
    {"name": "Research Group 1", "kind": "Individual", "is_default": True},
    {"name": "Research Group 2", "kind": "Lab", "is_default": False},
    {"name": "Research Group 3", "kind": "Lab", "is_default": False},
]

CURRENT_GROUP = {
    "name": "Research Group 1",
    "kind": "Individual",
    "is_default": True,
    "chemical_count": 3,
    "fish_line_count": 5,
    "submission_count": 2,
}
