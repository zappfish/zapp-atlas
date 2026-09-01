"""Post-process LinkML's ``gen-sqla`` output to fix self-referential relationships.

Why this exists
---------------
For a slot whose range is its own class (e.g. ``Genotype.background`` → ``Genotype``,
because a wild-type background *is* a line), ``gen-sqla`` emits::

    background_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("Genotype.id"))
    background: Mapped[Genotype | None] = relationship(foreign_keys=[background_id])

SQLAlchemy cannot infer the direction of a self-referential relationship from the
foreign key alone — both sides are the same table. Without ``remote_side`` it
resolves the relationship as ONETOMANY, which silently inverts the write: assigning
``line.background = AB`` sets ``AB.background_id = line.id`` instead of
``line.background_id = AB.id``. Because a single background is shared by many lines,
each assignment overwrites the last and every line but one silently loses its
background.

The fix is to declare the parent's primary key as the remote side, which makes it a
proper MANYTOONE::

    background: Mapped[Genotype | None] = relationship(foreign_keys=[background_id], remote_side=[id])

This reads the generated module on stdin and writes the corrected module to stdout,
so it can be piped straight from ``gen-sqla`` in the Makefile.
"""

from __future__ import annotations

import re
import sys

# `    background: Mapped[Genotype | None] = relationship(foreign_keys=[background_id])`
_REL = re.compile(
    r"^(?P<indent>\s+)(?P<attr>\w+):\s*Mapped\[(?P<target>\w+)\s*\|\s*None\]\s*=\s*"
    r"relationship\((?P<args>[^)]*)\)\s*$"
)
_CLASS = re.compile(r"^class\s+(?P<name>\w+)\s*\(")


def fix(source: str) -> tuple[str, list[str]]:
    """Add ``remote_side`` to scalar self-referential relationships.

    Returns the corrected source and a list of ``Class.attr`` that were patched.
    """
    out: list[str] = []
    patched: list[str] = []
    current: str | None = None

    for line in source.splitlines():
        m_cls = _CLASS.match(line)
        if m_cls:
            current = m_cls.group("name")

        m_rel = _REL.match(line)
        # Only scalar (Mapped[X | None]) relationships pointing at the enclosing
        # class are self-referential many-to-one. Multivalued ones are
        # Mapped[list[X]] and never match this pattern.
        if m_rel and current and m_rel.group("target") == current:
            args = m_rel.group("args").strip()
            if "remote_side" not in args:
                new_args = f"{args}, remote_side=[id]" if args else "remote_side=[id]"
                line = (
                    f"{m_rel.group('indent')}{m_rel.group('attr')}: "
                    f"Mapped[{current} | None] = relationship({new_args})"
                )
                patched.append(f"{current}.{m_rel.group('attr')}")

        out.append(line)

    return "\n".join(out) + "\n", patched


def main() -> int:
    source = sys.stdin.read()
    fixed, patched = fix(source)
    sys.stdout.write(fixed)
    for p in patched:
        print(f"  self-referential relationship patched with remote_side: {p}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
