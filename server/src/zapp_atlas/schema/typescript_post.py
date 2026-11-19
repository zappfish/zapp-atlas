"""Post-process ``gen-typescript`` output for the client.

Reads the generator's TypeScript on stdin and writes the client's copy on
stdout, given the schema it was generated from.

**Identifier aliases get their real type.** The generator declares an alias
for every class that has an identifier -- ``export type ResearchGroupId`` --
and uses it wherever another class refers to that one. Its template writes
every alias as ``string``. Ours are mostly integers, and the JSON Schema and
the server both say so, so a form bound to the alias would type-check and
then fail validation with "must be integer". The aliases of classes whose
identifier is a number are rewritten to ``number``; the rest are left alone.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from linkml_runtime import SchemaView
from linkml_runtime.utils.formatutils import camelcase

NUMERIC_RANGES = {"integer", "float", "double", "decimal"}


def numeric_identifier_aliases(schema_path: Path) -> set[str]:
    """The alias of every class whose identifier is a number."""
    view = SchemaView(str(schema_path))
    aliases = set()
    for class_name in view.all_classes():
        identifier = view.get_identifier_slot(class_name)
        if identifier is None:
            continue
        if view.induced_slot(identifier.name, class_name).range in NUMERIC_RANGES:
            # The generator's own naming: class name, then identifier slot.
            aliases.add(f"{camelcase(class_name)}{camelcase(identifier.name)}")
    return aliases


def type_identifier_aliases(source: str, numeric: set[str]) -> str:
    """Declare each alias in ``numeric`` as ``number`` instead of ``string``.

    Every alias has to be found. One that is not means the generator's output
    changed shape, and saying so beats quietly leaving the wrong type behind.
    """
    found = set()

    def retype(match: re.Match[str]) -> str:
        alias = match.group(1)
        if alias not in numeric:
            return match.group(0)
        found.add(alias)
        return f"export type {alias} = number;"

    source = re.sub(r"^export type (\w+) = string;$", retype, source, flags=re.MULTILINE)
    if missing := numeric - found:
        raise ValueError(f"no identifier alias to retype for: {sorted(missing)}")
    return source


def main() -> None:
    schema_path = Path(sys.argv[1])
    sys.stdout.write(
        type_identifier_aliases(sys.stdin.read(), numeric_identifier_aliases(schema_path))
    )


if __name__ == "__main__":
    main()
