"""The client's JSON Schema has to actually enforce the schema's class rules.

LinkML emits a rule that has no ``preconditions`` as a bare ``then`` with no
``if`` beside it. JSON Schema only applies ``then`` as the consequent of an
``if``, so such a rule validates nothing -- it is silently inert, and the
client's Ajv runs with ``strict: false``, which suppresses even the warning.
``json_schema_post`` hoists those, and these tests hold that in place.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zapp_atlas.schema.json_schema_post import hoist_unconditional_then

CLIENT_SCHEMA = Path(__file__).resolve().parents[2] / "client" / "src" / "schema" / "schema.json"


def _bare_thens(node: object, path: str = "$") -> list[str]:
    """Every location holding a ``then`` with no ``if`` to trigger it."""
    found = []
    if isinstance(node, dict):
        if "then" in node and "if" not in node:
            found.append(path)
        found += [p for k, v in node.items() for p in _bare_thens(v, f"{path}.{k}")]
    elif isinstance(node, list):
        found += [p for i, v in enumerate(node) for p in _bare_thens(v, f"{path}[{i}]")]
    return found


def test_hoists_a_rule_that_has_no_precondition() -> None:
    consequent = {"anyOf": [{"required": ["a"]}, {"required": ["b"]}]}

    assert hoist_unconditional_then({"then": consequent}) == consequent


def test_leaves_a_real_conditional_alone() -> None:
    conditional = {"if": {"required": ["x"]}, "then": {"required": ["y"]}}

    assert hoist_unconditional_then(dict(conditional)) == conditional


def test_reaches_rules_nested_in_all_of() -> None:
    # A class with more than one rule gets them wrapped in `allOf`.
    hoisted = hoist_unconditional_then({"allOf": [{"then": {"required": ["a"]}}]})

    assert hoisted == {"allOf": [{"required": ["a"]}]}


def test_refuses_to_hoist_over_an_existing_key() -> None:
    with pytest.raises(ValueError, match="required"):
        hoist_unconditional_then({"required": ["a"], "then": {"required": ["b"]}})


def test_the_generated_client_schema_has_no_inert_rules() -> None:
    schema = json.loads(CLIENT_SCHEMA.read_text())

    assert _bare_thens(schema) == []


def test_the_stressor_identity_rule_survives_as_a_real_constraint() -> None:
    """The rule this PR added must reach the client as something Ajv applies."""
    stressor = json.loads(CLIENT_SCHEMA.read_text())["$defs"]["StressorChemical"]

    alternatives = [
        set(branch.get("required", ()))
        for clause in stressor["allOf"]
        for branch in clause.get("anyOf", ())
    ]

    assert {"chemical_id"} in alternatives
    assert {"unrecognized_chemical_name"} in alternatives
