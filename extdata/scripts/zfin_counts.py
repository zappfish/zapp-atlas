# /// script
# requires-python = ">=3.12"
# dependencies = ["typer==0.19.2"]
# ///
"""Count how many times ZFIN curated each ZP term, from fish_to_phenotype.tsv.

Each row of that file is one curated statement (a fish, stage, environment,
and publication annotated with a ZP term), so a term's count is its number of
rows. Exact duplicate rows are counted once. Counts are not rolled up to
ancestor terms: a term's count is how often that exact EQ combination was
curated.
"""

import csv
from collections import Counter
from pathlib import Path
from typing import Annotated

import typer


def main(
    fish_to_phenotype: Annotated[Path, typer.Argument(help="ZP's fish_to_phenotype.tsv")],
    output: Annotated[Path, typer.Argument(help="TSV of zp_id and count")],
) -> None:
    seen: set[tuple[str, ...]] = set()
    counts: Counter[str] = Counter()
    with fish_to_phenotype.open(newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        zp_column = next(reader).index("zp_id")
        for row in reader:
            key = tuple(row)
            if key in seen:
                continue
            seen.add(key)
            counts[row[zp_column]] += 1

    with output.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(["zp_id", "count"])
        for zp_id in sorted(counts):
            writer.writerow([zp_id, counts[zp_id]])
    typer.echo(f"{output}: {len(counts)} terms from {len(seen)} distinct rows", err=True)


if __name__ == "__main__":
    typer.run(main)
