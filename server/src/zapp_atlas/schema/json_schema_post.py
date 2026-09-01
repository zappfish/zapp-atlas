"""Post-process ``gen-json-schema`` output for the client.

Reads the generator's JSON Schema on stdin and writes the client's copy on
stdout. Two things happen here that the generator does not do itself.

**Unconditional class rules are made effective.** A LinkML rule with
``postconditions`` and no ``preconditions`` is emitted as a bare ``then`` with
no ``if`` beside it. JSON Schema only applies ``then`` as the consequent of an
``if``, so a ``then`` on its own is ignored -- the constraint is silently
dropped rather than enforced. StressorChemical's "must have chemical_id or
unrecognized_chemical_name" rule is one of these. Hoisting the ``then`` in
place says the same thing unconditionally, which is what the rule means.
Rules that do carry a precondition already emit a real ``if``/``then`` pair
and are left alone.

**The do-not-edit notice is injected.** JSON has no comments, so it rides in
the standard ``$comment`` keyword as the first key.
"""

from __future__ import annotations

import json
import sys
from typing import Any

NOTICE = "GENERATED FILE. DO NOT EDIT. Regenerate with `make schema`."


def hoist_unconditional_then(node: Any) -> Any:
    """Replace every ``{"then": X}`` that has no ``if`` with ``X`` itself.

    Recurses through the whole document, so it applies wherever the generator
    puts a rule -- directly on a class, or inside the ``allOf`` it uses once a
    class has more than one rule.
    """
    if isinstance(node, list):
        return [hoist_unconditional_then(item) for item in node]
    if not isinstance(node, dict):
        return node

    node = {key: hoist_unconditional_then(value) for key, value in node.items()}
    if "then" in node and "if" not in node:
        consequent = node.pop("then")
        if not isinstance(consequent, dict):  # nothing sensible to hoist
            return node
        # Anything alongside the rule (there normally is nothing) is kept.
        overlap = node.keys() & consequent.keys()
        if overlap:
            raise ValueError(f"cannot hoist `then`, would clobber: {sorted(overlap)}")
        node.update(consequent)
    return node


def main() -> None:
    schema = json.load(sys.stdin)
    schema = hoist_unconditional_then(schema)
    json.dump({"$comment": NOTICE, **schema}, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
