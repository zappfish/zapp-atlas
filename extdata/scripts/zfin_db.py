# /// script
# requires-python = ">=3.12"
# dependencies = ["typer==0.19.2"]
# ///
"""Build zfin.db: ZFIN's registered alleles, genotypes, fish and wild-type
lines, for the server's fish lookups (``zapp_atlas/zfin.py``).

Reads five of ZFIN's bulk downloads. All are tab-separated with no header
row; the column layouts below are from https://zfin.org/downloads. Ids are
stored as CURIEs (``ZFIN:ZDB-ALT-...``), the form the schema's patterns want.

``features.txt`` -- one row per (allele, construct), so an allele carrying
several constructs (a co-injected line) repeats; rows are aggregated by id::

    0 feature id (ZDB-ALT-)   1 SO id              2 abbreviation (symbol)
    3 name                    4 type label         5 mutagen
    6 mutagee                 7 construct id       8 construct name
    9 construct SO id        10 TALEN/CRISPR id   11 TALEN/CRISPR name

``features-affected-genes.txt`` -- one row per (allele, gene). 42 columns,
of which the first 7 are read; only ``is allele of`` rows link an allele to
a gene (the others are ``markers missing`` / ``markers moved``)::

    0 feature id   1 SO id   2 abbreviation   3 gene symbol   4 gene id
    5 gene SO id   6 relationship

``wildtypes_fish.txt`` -- the wild-type lines::

    0 fish id   1 name   2 abbreviation   3 genotype id

``genotype_features.txt`` -- one row per (genotype, allele, construct);
aggregated by (genotype, allele). The unique name encodes zygosity per
allele as ``symbol[fish,mother,father]`` (``U`` unknown, ``1`` heterozygous,
``2`` homozygous, ``C`` complex, ``W`` wild type), followed by the
background; column 10 spells out the fish's own zygosity::

    0 genotype id             1 name (HTML <sup>)      2 unique name
    3 allele id               4 allele name            5 allele abbreviation
    6 allele type             7 allele display type    8 gene/construct symbol
    9 gene/construct id      10 zygosity              11 construct name
   12 construct id

``fish_components_fish.txt`` -- one row per (fish, affector, gene), where an
affector is an allele or a transient reagent (morpholino, CRISPR, TALEN);
aggregated by (fish, affector). A fish can list two backgrounds::

    0 fish id         1 fish name        2 gene id         3 gene symbol
    4 affector id     5 affector symbol  6 construct id    7 construct symbol
    8 background id   9 background name 10 genotype id    11 genotype name
"""

import csv
import re
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Annotated

import typer

INPUTS = (
    "features.txt",
    "features-affected-genes.txt",
    "wildtypes_fish.txt",
    "genotype_features.txt",
    "fish_components_fish.txt",
)

SO_TRANSGENIC_INSERTION = "SO:0001218"
ALLELE_OF = "is allele of"
NOT_SPECIFIED = ("", "not specified")

# Zygosity codes in a genotype's unique name -> the words column 10 uses.
ZYGOSITY_CODES = {
    "U": "unknown",
    "1": "heterozygous",
    "2": "homozygous",
    "C": "complex",
    "W": "wild type",
}
UNIQUE_NAME_GROUP = re.compile(r"(\S+?)\[([^\]]*)\]")

# Transient reagents, by the id prefix ZFIN gives them.
REAGENT_KINDS = {
    "ZDB-MRPHLNO-": "morpholino",
    "ZDB-CRISPR-": "crispr",
    "ZDB-TALEN-": "talen",
}

HTML_TAG = re.compile(r"<[^>]+>")

SCHEMA = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID;

CREATE TABLE wildtype (
    fish_id TEXT PRIMARY KEY,
    genotype_id TEXT NOT NULL,
    name TEXT NOT NULL,
    abbreviation TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE background (
    background_id TEXT PRIMARY KEY,  -- a wild-type genotype
    name TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE allele (
    allele_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,              -- differs from symbol for deficiencies etc.
    so_id TEXT,                      -- a few rows have none
    type_label TEXT NOT NULL,        -- ZFIN's human-readable type
    mutagen TEXT,
    is_transgenic INTEGER NOT NULL
) WITHOUT ROWID;
CREATE TABLE allele_gene (
    allele_id TEXT NOT NULL,
    gene_id TEXT NOT NULL,
    gene_symbol TEXT NOT NULL,
    PRIMARY KEY (allele_id, gene_id)
) WITHOUT ROWID;
CREATE INDEX allele_gene_gene ON allele_gene (gene_id);
CREATE TABLE allele_construct (
    allele_id TEXT NOT NULL,
    construct_id TEXT NOT NULL,
    construct_name TEXT NOT NULL,
    PRIMARY KEY (allele_id, construct_id)
) WITHOUT ROWID;

CREATE TABLE genotype (
    genotype_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,              -- as ZFIN writes it, with <sup> markup
    name_plain TEXT NOT NULL,        -- markup stripped
    unique_name TEXT                 -- zygosity-encoded; NULL for wild types
) WITHOUT ROWID;
CREATE TABLE genotype_allele (
    genotype_id TEXT NOT NULL,
    allele_id TEXT NOT NULL,
    allele_symbol TEXT NOT NULL,
    zygosity TEXT NOT NULL,
    mother_zygosity TEXT,
    father_zygosity TEXT,
    PRIMARY KEY (genotype_id, allele_id)
) WITHOUT ROWID;
CREATE INDEX genotype_allele_allele ON genotype_allele (allele_id);
CREATE TABLE genotype_background (
    genotype_id TEXT NOT NULL,
    background_id TEXT NOT NULL,
    PRIMARY KEY (genotype_id, background_id)
) WITHOUT ROWID;

CREATE TABLE fish (
    fish_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    name_plain TEXT NOT NULL,
    genotype_id TEXT NOT NULL
) WITHOUT ROWID;
CREATE INDEX fish_genotype ON fish (genotype_id);
CREATE TABLE fish_background (
    fish_id TEXT NOT NULL,
    background_id TEXT NOT NULL,
    PRIMARY KEY (fish_id, background_id)
) WITHOUT ROWID;

CREATE TABLE reagent (
    reagent_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    kind TEXT NOT NULL               -- morpholino | crispr | talen
) WITHOUT ROWID;
CREATE TABLE reagent_gene (
    reagent_id TEXT NOT NULL,
    gene_id TEXT NOT NULL,
    gene_symbol TEXT NOT NULL,
    PRIMARY KEY (reagent_id, gene_id)
) WITHOUT ROWID;
CREATE TABLE fish_reagent (
    fish_id TEXT NOT NULL,
    reagent_id TEXT NOT NULL,
    PRIMARY KEY (fish_id, reagent_id)
) WITHOUT ROWID;
CREATE INDEX fish_reagent_reagent ON fish_reagent (reagent_id);

-- Allele autocomplete: a query matches the start of any word in these.
CREATE VIRTUAL TABLE allele_fts USING fts5(
    allele_id UNINDEXED, symbol, name, genes, constructs,
    tokenize = 'unicode61 remove_diacritics 2'
);
"""


def curie(zdb_id: str) -> str:
    return f"ZFIN:{zdb_id}"


def plain(name: str) -> str:
    return HTML_TAG.sub("", name)


def rows(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.reader(f, delimiter="\t"):
            if row:
                yield row


def parental_zygosity(unique_name: str, symbols: set[str]) -> dict[str, tuple[str, str]]:
    """symbol -> (mother, father) zygosity from a genotype's unique name, or
    {} when the name's groups don't line up one-to-one with the alleles."""
    groups = UNIQUE_NAME_GROUP.findall(unique_name)
    found = {symbol: triple.split(",") for symbol, triple in groups}
    if set(found) != symbols or any(len(t) != 3 for t in found.values()):
        return {}
    try:
        return {symbol: (ZYGOSITY_CODES[t[1]], ZYGOSITY_CODES[t[2]]) for symbol, t in found.items()}
    except KeyError:
        return {}


def load_wildtypes(path: Path, db: sqlite3.Connection) -> None:
    db.executemany(
        "INSERT INTO wildtype VALUES (?, ?, ?, ?)",
        ((curie(r[0]), curie(r[3]), r[1], r[2] or r[1]) for r in rows(path)),
    )
    # Wild-type lines are genotypes and fish in their own right, so they can
    # be fetched by either id like any other.
    db.execute("INSERT OR IGNORE INTO genotype SELECT genotype_id, name, name, NULL FROM wildtype")
    db.execute("INSERT INTO fish SELECT fish_id, name, name, genotype_id FROM wildtype")


def load_alleles(features: Path, affected_genes: Path, db: sqlite3.Connection) -> None:
    alleles: dict[str, list] = {}
    constructs: dict[tuple[str, str], str] = {}
    for r in rows(features):
        if not r[0].startswith("ZDB-ALT-") or not r[2]:
            continue
        allele_id = curie(r[0])
        so_id = r[1] or None
        mutagen = None if r[5] in NOT_SPECIFIED else r[5]
        is_transgenic = so_id == SO_TRANSGENIC_INSERTION or bool(r[7])
        entry = alleles.setdefault(
            allele_id, [allele_id, r[2], r[3] or r[2], so_id, r[4] or "Unknown", mutagen, False]
        )
        entry[5] = entry[5] or mutagen
        entry[6] = entry[6] or is_transgenic
        if r[7] and r[8]:
            constructs.setdefault((allele_id, curie(r[7])), r[8])
    db.executemany("INSERT INTO allele VALUES (?, ?, ?, ?, ?, ?, ?)", alleles.values())
    db.executemany(
        "INSERT INTO allele_construct VALUES (?, ?, ?)",
        ((a, c, name) for (a, c), name in constructs.items()),
    )
    db.executemany(
        "INSERT OR IGNORE INTO allele_gene VALUES (?, ?, ?)",
        (
            (curie(r[0]), curie(r[4]), r[3])
            for r in rows(affected_genes)
            if len(r) > 6 and r[6] == ALLELE_OF and r[3] and r[4]
        ),
    )


def load_genotypes(path: Path, db: sqlite3.Connection) -> None:
    genotypes: dict[str, tuple[str, str]] = {}  # id -> (name, unique name)
    alleles: dict[str, dict[str, tuple[str, str]]] = defaultdict(
        dict
    )  # id -> allele -> (symbol, zygosity)
    for r in rows(path):
        if not r[0].startswith("ZDB-GENO-") or not r[3].startswith("ZDB-ALT-"):
            continue
        genotype_id = curie(r[0])
        genotypes.setdefault(genotype_id, (r[1], r[2]))
        alleles[genotype_id].setdefault(curie(r[3]), (r[5] or r[4], r[10] or "unknown"))

    db.executemany(
        "INSERT OR REPLACE INTO genotype VALUES (?, ?, ?, ?)",
        ((g, name, plain(name), unique) for g, (name, unique) in genotypes.items()),
    )
    for genotype_id, (_, unique_name) in genotypes.items():
        carried = alleles[genotype_id]
        parents = parental_zygosity(unique_name, {symbol for symbol, _ in carried.values()})
        db.executemany(
            "INSERT INTO genotype_allele VALUES (?, ?, ?, ?, ?, ?)",
            (
                (genotype_id, allele_id, symbol, zygosity, *parents.get(symbol, (None, None)))
                for allele_id, (symbol, zygosity) in carried.items()
            ),
        )


def load_fish(path: Path, db: sqlite3.Connection) -> None:
    fish: dict[str, tuple[str, str]] = {}
    backgrounds: dict[str, str] = {}
    fish_backgrounds: set[tuple[str, str]] = set()
    genotype_backgrounds: set[tuple[str, str]] = set()
    reagents: dict[str, tuple[str, str]] = {}
    reagent_genes: set[tuple[str, str, str]] = set()
    fish_reagents: set[tuple[str, str]] = set()
    allele_genes: set[tuple[str, str, str]] = set()
    for r in rows(path):
        if not r[0].startswith("ZDB-FISH-") or not r[10].startswith("ZDB-GENO-"):
            continue
        fish_id, genotype_id = curie(r[0]), curie(r[10])
        fish.setdefault(fish_id, (r[1], genotype_id))
        if r[8]:
            background_id = curie(r[8])
            backgrounds.setdefault(background_id, r[9] or r[8])
            fish_backgrounds.add((fish_id, background_id))
            genotype_backgrounds.add((genotype_id, background_id))
        affector_id, affector_symbol = r[4], r[5]
        gene = (curie(r[2]), r[3]) if r[2] and r[3] else None
        kind = next((k for p, k in REAGENT_KINDS.items() if affector_id.startswith(p)), None)
        if kind:
            reagent_id = curie(affector_id)
            reagents.setdefault(reagent_id, (affector_symbol or affector_id, kind))
            fish_reagents.add((fish_id, reagent_id))
            if gene:
                reagent_genes.add((reagent_id, *gene))
        elif affector_id.startswith("ZDB-ALT-") and gene:
            allele_genes.add((curie(affector_id), *gene))

    db.executemany(
        "INSERT OR IGNORE INTO fish VALUES (?, ?, ?, ?)",
        ((f, name, plain(name), g) for f, (name, g) in fish.items()),
    )
    db.executemany("INSERT INTO background VALUES (?, ?)", backgrounds.items())
    db.executemany("INSERT INTO fish_background VALUES (?, ?)", sorted(fish_backgrounds))
    db.executemany("INSERT INTO genotype_background VALUES (?, ?)", sorted(genotype_backgrounds))
    db.executemany(
        "INSERT INTO reagent VALUES (?, ?, ?)",
        ((rid, symbol, kind) for rid, (symbol, kind) in reagents.items()),
    )
    db.executemany("INSERT INTO reagent_gene VALUES (?, ?, ?)", sorted(reagent_genes))
    db.executemany("INSERT INTO fish_reagent VALUES (?, ?)", sorted(fish_reagents))
    # Transgenic insertions have no "is allele of" row; some carry a gene here.
    known = {allele_id for (allele_id,) in db.execute("SELECT allele_id FROM allele")}
    db.executemany(
        "INSERT OR IGNORE INTO allele_gene VALUES (?, ?, ?)",
        (row for row in sorted(allele_genes) if row[0] in known),
    )


def build_fts(db: sqlite3.Connection) -> None:
    db.execute(
        """
        INSERT INTO allele_fts (allele_id, symbol, name, genes, constructs)
        SELECT a.allele_id, a.symbol, a.name,
               (SELECT group_concat(gene_symbol, ' ') FROM allele_gene g WHERE g.allele_id = a.allele_id),
               (SELECT group_concat(construct_name, ' ') FROM allele_construct c WHERE c.allele_id = a.allele_id)
        FROM allele a
        """
    )


def write_meta(db: sqlite3.Connection, zfin_date: str) -> dict[str, int]:
    counts = {
        table: db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        for table in ("wildtype", "allele", "genotype", "fish", "reagent")
    }
    db.execute("INSERT INTO meta VALUES ('zfin_date', ?)", (zfin_date,))
    db.executemany(
        "INSERT INTO meta VALUES (?, ?)", ((f"{t}_count", str(n)) for t, n in counts.items())
    )
    return counts


def main(
    output: Annotated[Path, typer.Argument(help="SQLite database to write")],
    zfin_dir: Annotated[Path, typer.Argument(help="Directory holding the ZFIN downloads")],
    zfin_date: Annotated[str, typer.Option(help="The ZFIN archive date the files are from")],
) -> None:
    missing = [name for name in INPUTS if not (zfin_dir / name).is_file()]
    if missing:
        raise typer.BadParameter(f"missing in {zfin_dir}: {', '.join(missing)}")

    output.unlink(missing_ok=True)
    db = sqlite3.connect(output)
    db.execute("PRAGMA journal_mode = OFF")
    db.execute("PRAGMA synchronous = OFF")
    db.executescript(SCHEMA)
    with db:
        load_alleles(zfin_dir / INPUTS[0], zfin_dir / INPUTS[1], db)
        load_wildtypes(zfin_dir / INPUTS[2], db)
        load_genotypes(zfin_dir / INPUTS[3], db)
        load_fish(zfin_dir / INPUTS[4], db)
        build_fts(db)
        counts = write_meta(db, zfin_date)
    db.execute("VACUUM")
    db.close()
    typer.echo(
        f"{output}: " + ", ".join(f"{n} {table}" for table, n in counts.items()),
        err=True,
    )


if __name__ == "__main__":
    typer.run(main)
