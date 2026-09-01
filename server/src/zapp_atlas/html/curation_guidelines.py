"""Content for the curation guidelines page.

Held here rather than in the database: these are editorial guidance that
changes when the curation team revises it, not curated records. The page
groups them into filterable categories, each holding numbered entries.
"""

from __future__ import annotations

GROUPS: list[dict] = [
    {
        "slug": "image",
        "label": "Image",
        "title": "Image-related annotations",
        "entries": [
            {
                "summary": "The phenotype you pick should be visible on the image",
                "body": (
                    "If you submit an image, the phenotype you pick should be "
                    "visible on the image you submit. For example, if you are "
                    "submitting an overview image of an entire zebrafish embryo "
                    "(say a 24 or 48 hpf old embryo), submit phenotypes "
                    "concerning the entire embryo: shortened or curved body "
                    "axis, small head/microcephalus, no melanocytes/pigmentation."
                ),
            },
            {
                "summary": "Do not annotate phenotypes that are not visible",
                "body": (
                    "Phenotypes absent from the submitted image should not be "
                    "annotated on it."
                ),
            },
            {
                "summary": "Only one fish in an image",
                "body": (
                    "If a fish has three phenotypes, annotate all three if they "
                    "are all visible in that image. Upload additional images at "
                    "higher magnification or in different orientations to cover "
                    "the rest."
                ),
            },
            {
                "summary": "Include an image of a control fish",
                "body": "Submit a matching control alongside the treated fish.",
            },
            {
                "summary": "Match imaging conditions between treated and control",
                "body": (
                    "Magnification, laser power, brightness, and any other "
                    "imaging condition used for the treated fish must be the "
                    "same for the control fish."
                ),
            },
            {
                "summary": "Note the size of the scale bar if present",
                "body": "Where the image carries a scale bar, record its size.",
            },
            {
                "summary": "Include details of magnification used during imaging",
                "body": "Record the magnification the image was captured at.",
            },
        ],
    },
    {
        "slug": "phenotype",
        "label": "Phenotype",
        "title": "Phenotype-related annotations",
        "entries": [
            {
                "summary": "Always use the phenotype picker to select terms",
                "body": (
                    "Check for synonyms first, and only request a new phenotype "
                    "term if the exact concept is unavailable."
                ),
            },
            {
                "summary": "Choose the most granular term available",
                "body": (
                    "Pick the most specific phenotype term in the Phenotype "
                    "Picker. This maximizes the atlas's utility for the "
                    "community."
                ),
            },
            {
                "summary": "Include the age of fish in submitted images",
                "body": "For example: 24 hpf, 5 dpf.",
            },
            {
                "summary": "Include the background strain of fish used",
                "body": (
                    "Different strains can experience different effects and "
                    "phenotypes in response to drugs. The Tuebingen (TU) strain, "
                    "for instance, is more resistant to ethanol-induced "
                    "craniofacial defects than the AB strain."
                ),
            },
        ],
    },
    {
        "slug": "exposure",
        "label": "Exposure",
        "title": "Exposure-related annotations",
        "entries": [
            {
                "summary": "Identify the chemical by ID, not just by name",
                "body": "A name alone is ambiguous; record the identifier.",
            },
            {
                "summary": "Include the concentration of the chemical",
                "body": "Record the concentration the fish were exposed to.",
            },
            {
                "summary": "Include the route of exposure",
                "body": "The route of exposure is required.",
            },
            {
                "summary": "Indicate when exposure started and stopped",
                "body": (
                    "Give the age of the fish when exposure began and, if "
                    "applicable, when it ended."
                ),
            },
            {
                "summary": "State whether exposure was continuous or repeated",
                "body": "Record which of the two applies.",
            },
        ],
    },
    {
        "slug": "misc",
        "label": "Miscellaneous",
        "title": "Miscellaneous",
        "entries": [
            {"summary": "Chemical screen", "body": ""},
            {"summary": "Bulk submission", "body": "To be determined."},
        ],
    },
]


def entry_count() -> int:
    return sum(len(group["entries"]) for group in GROUPS)
