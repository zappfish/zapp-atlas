"""Where the LinkML schema lives, and one shared view of it."""

from functools import cache
from pathlib import Path

from linkml_runtime import SchemaView

SCHEMA_PATH = Path(__file__).resolve().parent / "zebrafish_toxicology_atlas_schema.yaml"


@cache
def schema_view() -> SchemaView:
    return SchemaView(str(SCHEMA_PATH))
