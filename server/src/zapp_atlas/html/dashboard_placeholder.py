"""Static data for the research group dashboard.

Data is keyed by group id, shaped like the group-scoped API responses:
each group has its own fish tank, chemical cabinet, and submissions.
"""

from __future__ import annotations


def _fish(zf_id, name, *, background=None, mutations=(), transgenes=()):
    return {
        "zf_id": zf_id,
        "name": name,
        "background": background,
        "mutations": list(mutations),
        "transgenes": list(transgenes),
    }


_MUT = {"allele": "fh111", "zygosity": "homo", "gene": "snapc3b"}
_TG = {"allele": "w200Tg", "zygosity": "unknown", "construct": "Tg(mpeg1:YFP)"}


# The sidebar list. `dots` are small per-group status indicators.
GROUPS = [
    {"id": 1, "name": "Research Group 1", "kind": "Individual", "is_default": True,
     "owner": "Dr. A. Researcher", "dots": ["green", "green", "orange"]},
    {"id": 2, "name": "Research Group 2", "kind": "Lab", "is_default": False,
     "owner": "Dr. B. Lead", "dots": ["green", "green", "green", "orange"]},
    {"id": 3, "name": "Research Group 3", "kind": "Lab", "is_default": False,
     "owner": "Dr. C. Head", "dots": ["green", "green", "green", "green", "orange"]},
]


# Per-group tank / cabinet / submissions, keyed by group id.
_GROUP_DATA = {
    1: {
        "fish_tank": [
            _fish("ZF-1042", "snapc1bfh111/fh111; w200Tg (AB)",
                  background="AB", mutations=[_MUT], transgenes=[_TG]),
            _fish("ZF-1107", "snapc1bfh111/fh111; w200Tg (AB)",
                  background="AB", mutations=[_MUT], transgenes=[_TG]),
            _fish("ZF-0891", "snapc1bfh111/fh111; w200Tg (AB)",
                  background="AB", mutations=[_MUT]),
            _fish("ZF-0234", "pax2a^th16/th16", background="AB", transgenes=[_TG]),
        ],
        "cabinet": [
            {"abbr": "EtOH", "name": "Ethanol", "manufacturer": "Sigma-Aldrich",
             "chemical_id": "CHEBI:16236"},
            {"abbr": "CdCl2", "name": "Cadmium chloride", "manufacturer": "Sigma-Aldrich",
             "chemical_id": "CHEBI:35456"},
            {"abbr": "VPA", "name": "Valproic acid", "manufacturer": "Sigma-Aldrich",
             "chemical_id": "CHEBI:39867"},
        ],
        "submissions": [
            {"title": "sox2 expression — 24 hpf neural tube",
             "status": "Published", "date": "2026-05-14"},
            {"title": "pax2a optic cup ISH dataset",
             "status": "In Progress", "date": "2026-06-01"},
        ],
    },
    2: {
        "fish_tank": [
            _fish("ZF-2200", "TU wild type", background="TU"),
            _fish("ZF-2201", "casper (roy; nacre)", background="AB",
                  mutations=[{"allele": "roy", "zygosity": "homo", "gene": "roya9"}]),
        ],
        "cabinet": [
            {"abbr": "DMSO", "name": "Dimethyl sulfoxide", "manufacturer": "Fisher",
             "chemical_id": "CHEBI:28262"},
        ],
        "submissions": [
            {"title": "casper pigmentation baseline",
             "status": "In Progress", "date": "2026-06-20"},
        ],
    },
    3: {
        "fish_tank": [],
        "cabinet": [],
        "submissions": [],
    },
}


def total_submissions():
    """The user's submission count across all groups (for the sidebar badge)."""
    return sum(len(d["submissions"]) for d in _GROUP_DATA.values())


def all_submissions():
    """Every submission across the user's groups, each tagged with its group,
    newest first — for the My Submissions view.
    """
    items = []
    for group in GROUPS:
        for sub in _GROUP_DATA.get(group["id"], {}).get("submissions", []):
            items.append({**sub, "group_name": group["name"], "group_id": group["id"]})
    return sorted(items, key=lambda s: s["date"], reverse=True)


def get_group(group_id):
    """The group's sidebar entry, or None if unknown."""
    return next((g for g in GROUPS if g["id"] == group_id), None)


def get_group_view(group_id):
    """One group with its counts and its tank, cabinet, and submissions.

    Returns None for an unknown group.
    """
    group = get_group(group_id)
    if group is None:
        return None
    data = _GROUP_DATA.get(group_id, {"fish_tank": [], "cabinet": [], "submissions": []})
    return {
        "groups": GROUPS,
        # "My Submissions" is the user's total across all groups, not this group's.
        "my_submissions_count": total_submissions(),
        "group": {
            **group,
            "chemical_count": len(data["cabinet"]),
            "fish_line_count": len(data["fish_tank"]),
            "submission_count": len(data["submissions"]),
        },
        "fish_tank": data["fish_tank"],
        "cabinet": data["cabinet"],
        "submissions": data["submissions"],
    }
