"""Site navigation structure.

The header renders from this, so adding an item or a dropdown entry is a data
change rather than a template change. An entry with `children` becomes a dropdown;
one without becomes a plain link. `external` marks a link that leaves the app.
"""

from __future__ import annotations

ITEMS: list[dict] = [
    {
        "label": "Resources",
        "children": [
            {"label": "Curation Guidelines", "href": "/curation-guidelines"},
            {
                "label": "Data Governance",
                "href": "https://zappfish.org/ZAPPGovernance/",
                "external": True,
            },
            {
                "label": "Project FAQ",
                "href": "https://zappfish.org/faqs",
                "external": True,
            },
            {
                "label": "Contact Us",
                "href": "https://zappfish.org/contact",
                "external": True,
            },
        ],
    },
    {"label": "Downloads", "href": "/downloads"},
    {"label": "Help", "href": "/help"},
]
