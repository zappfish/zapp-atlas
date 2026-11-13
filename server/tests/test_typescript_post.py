"""The client's identifier aliases have to say what an identifier really is.

``gen-typescript`` writes every ``<Class>Id`` alias as ``string``. Ours are
mostly integers, so ``typescript_post`` retypes them; these tests hold that in
place, and hold the generated file to the schema it came from.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from zapp_atlas.schema.constraints import SCHEMA_PATH
from zapp_atlas.schema.typescript_post import numeric_identifier_aliases, type_identifier_aliases

CLIENT_TYPES = Path(__file__).resolve().parents[2] / "client" / "src" / "schema" / "index.ts"

GENERATED = """\
export type StudyId = string;
export type PhenotypeTermTermUri = string;
export interface Study {
    id: number,
}
"""


def test_retypes_only_the_aliases_it_is_given() -> None:
    retyped = type_identifier_aliases(GENERATED, {"StudyId"})

    assert "export type StudyId = number;" in retyped
    assert "export type PhenotypeTermTermUri = string;" in retyped
    assert "    id: number," in retyped


def test_an_alias_that_cannot_be_found_is_an_error() -> None:
    with pytest.raises(ValueError, match="ExperimentId"):
        type_identifier_aliases(GENERATED, {"StudyId", "ExperimentId"})


def test_the_generated_aliases_agree_with_the_schema() -> None:
    declared = dict(
        re.findall(r"^export type (\w+) = (\w+);$", CLIENT_TYPES.read_text(), re.MULTILINE)
    )
    numeric = numeric_identifier_aliases(SCHEMA_PATH)

    assert "ResearchGroupId" in numeric
    assert {alias for alias, kind in declared.items() if kind == "number"} == numeric
    # Ontology terms are identified by CURIE, which is text.
    assert declared["PhenotypeTermTermUri"] == "string"
