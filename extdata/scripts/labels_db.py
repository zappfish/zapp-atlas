# /// script
# requires-python = ">=3.12"
# dependencies = ["typer==0.19.2"]
# ///
"""Build labels.db, the server's CURIE -> label lookup table.

Reads ROBOT `export` TSVs with ID and LABEL columns. Rows without a label are
skipped. If two inputs label the same ID, the first one given wins.
"""

import csv
import sqlite3
from pathlib import Path
from typing import Annotated

import typer


def main(
    output: Annotated[Path, typer.Argument(help="SQLite database to write")],
    exports: Annotated[list[Path], typer.Argument(help="ROBOT export TSVs (ID, LABEL)")],
) -> None:
    labels: dict[str, str] = {}
    for export in exports:
        with export.open(newline="") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                if row["LABEL"]:
                    labels.setdefault(row["ID"], row["LABEL"])

    output.unlink(missing_ok=True)
    with sqlite3.connect(output) as db:
        db.execute("CREATE TABLE term (id TEXT PRIMARY KEY, label TEXT NOT NULL) WITHOUT ROWID")
        db.executemany("INSERT INTO term VALUES (?, ?)", sorted(labels.items()))
    db.close()
    typer.echo(f"{output}: {len(labels)} labels", err=True)


if __name__ == "__main__":
    typer.run(main)
