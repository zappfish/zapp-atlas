"""Ontology term labels, from the extdata bundle's labels.db.

The table holds a label for every ZP, ZFA, and ChEBI term in the bundle (ZP
terms under their ZAPP preferred labels, as the phenotype picker shows
them). Lookups are primary-key reads on a read-only SQLite file, so they are
cheap enough to make per term while rendering.

Terms the table doesn't know -- obsolete ChEBI terms, other ontologies, or
every term when no bundle is installed -- have no label. Use ``label`` where
the caller wants to know that, and ``label_or_curie`` where it just needs
something to show.

Routes get the app's instance with the ``TermLabels`` dependency.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Annotated

from fastapi import Depends, Request

logger = logging.getLogger(__name__)


class Labels:
    def __init__(self, db_path: Path):
        self._db: sqlite3.Connection | None = None
        if not db_path.is_file():
            logger.warning(
                "Term labels not found at %s; terms will show as CURIEs. "
                "Build the extdata bundle with `just extdata`.",
                db_path,
            )
            return
        # immutable=1: the file never changes while the app runs, so SQLite
        # can skip locking. One connection is shared across request threads,
        # which the sqlite3 module allows when built thread-safe
        # (sqlite3.threadsafety == 3, the default).
        self._db = sqlite3.connect(
            f"{db_path.resolve().as_uri()}?mode=ro&immutable=1",
            uri=True,
            check_same_thread=False,
        )

    def label(self, curie: str) -> str | None:
        """The term's label, or None if the table has none for it."""
        if self._db is None:
            return None
        row = self._db.execute("SELECT label FROM term WHERE id = ?", (curie,)).fetchone()
        return row[0] if row else None

    def label_or_curie(self, curie: str) -> str:
        """The term's label, falling back to the CURIE itself."""
        return self.label(curie) or curie


def get_labels(request: Request) -> Labels:
    return request.app.state.labels


TermLabels = Annotated[Labels, Depends(get_labels)]
