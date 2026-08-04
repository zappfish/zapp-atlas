"""Static data for the public phenotype atlas home page.

Shaped like the search API responses: a stats summary, a page of phenotype
records, the facet groups for the filter sidebar, and the active filter chips.
"""

from __future__ import annotations

# Summary shown in the banner stats bar.
ATLAS_STATS = {
    "records": "XXX,XXXX",
    "labs": 55,
    "contributors": "14 labs",
    "last_updated": "12 May 2026",
    "license": "CC BY 4.0",
    "cite": "doi.org/10.x/zapp",
}

TITLE = "Zebrafish toxicology phenotype reference"
DESCRIPTION = (
    "A community-curated visual reference of zebrafish phenotypes arising from "
    "toxicological exposure. Each record links a chemical, dose, and "
    "developmental stage to annotated images, with provenance traceable to the "
    "contributing lab and publication."
)


def _record(record_id, image, phenotypes, *, chemical, fish, study_id, age):
    return {
        "id": record_id,
        "image": image,
        "phenotypes": list(phenotypes),
        "chemical": chemical,
        "fish": fish,
        "study_id": study_id,
        "age": age,
    }


# None renders the neutral thumbnail placeholder; a URL renders the image.
_IMG = None

# Records cycle through these value sets so the sample spans multiple
# chemicals, fish lines, developmental stages, and phenotype counts.
_CHEMICALS = ["Ethanol", "Cadmium", "Bisphenol A", "Nicotine", "Retinoic acid"]
_FISH = ["AB", "TU", "WIK", "TL"]
_AGES = ["5 hpf", "15 hpf", "20 hpf", "24 hpf", "48 hpf"]
_PHENOTYPE_SETS = [
    ["Tail Malformation"],
    ["Tail Malformation", "Curved tail", "Pericardial edema", "Yolk defect"],
    ["Pericardial edema"],
    ["Abnormal Fin Morphology", "Curved tail"],
    ["Absent Swim Bladder"],
    ["Abnormal Head Morphology", "Yolk defect"],
]

RECORDS = [
    _record(
        f"r-{i:02d}", _IMG, _PHENOTYPE_SETS[i % len(_PHENOTYPE_SETS)],
        chemical=_CHEMICALS[i % len(_CHEMICALS)],
        fish=_FISH[i % len(_FISH)],
        study_id=f"S-{100 + i}",
        age=_AGES[i % len(_AGES)],
    )
    for i in range(1, 41)
]

# Records served per page.
PAGE_SIZE = 12
TOTAL_RESULTS = len(RECORDS)


def page(number: int = 1):
    """Return one page of records plus pager state for a 1-based page number.

    Numbers outside the valid range are clamped to the first or last page.
    """
    total_pages = max(1, -(-TOTAL_RESULTS // PAGE_SIZE))  # ceil division
    number = max(1, min(number, total_pages))
    start = (number - 1) * PAGE_SIZE
    return {
        "records": RECORDS[start : start + PAGE_SIZE],
        "current_page": number,
        "total_pages": total_pages,
    }


# Sidebar filter facets. `open` sets the initial expanded state; `searchable`
# adds a search box within the group.
FACETS = [
    {
        "key": "phenotype", "label": "Phenotype", "open": True, "searchable": True,
        "options": [
            {"label": "abnormal head morph", "checked": True},
            {"label": "Abnormal Fin Morphology", "checked": True},
            {"label": "Abnormal Body Curvature", "checked": False},
            {"label": "Absent Swim Bladder", "checked": False},
        ],
    },
    {"key": "anatomical", "label": "Anatomical Structure", "open": False, "options": []},
    {"key": "chemical", "label": "Chemical", "open": False, "options": []},
    {
        "key": "age", "label": "Age/Stage", "open": True, "searchable": True,
        "options": [
            {"label": "24 hpf", "checked": True, "count": 24},
            {"label": "20 hpf", "checked": False, "count": 14},
            {"label": "15 hpf", "checked": False, "count": 5},
            {"label": "5 hpf", "checked": False, "count": 2},
        ],
    },
    {"key": "fish", "label": "Fish", "open": False, "options": []},
    {"key": "provenance", "label": "Provenance", "open": False, "options": []},
]

# Currently-applied filters, shown as removable chips above the results.
ACTIVE_FILTERS = [
    "abnormal head morph",
    "Abnormal Fin Morphology",
    "24 hpf",
]

SORT_OPTIONS = ["Relevance", "Newest", "Oldest"]
