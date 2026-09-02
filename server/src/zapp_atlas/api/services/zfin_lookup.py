"""Read-only lookups over ZFIN's bulk-download reference files.

Backs the fish widget's "type a symbol, get the record" path: a curator types
an allele symbol (``fh111``), a gene (``fgf8a``), or a construct fragment
(``mpeg1:YFP``) and gets back everything the data model wants — symbol,
ZDB-ALT id, alteration type, affected gene, construct — so the ZFIN
identifiers attach without the curator ever seeing an identifier field.

Three files from https://zfin.org/downloads (fetched by ``just fetch-zfin``
into ``settings.zfin_data_dir``; never committed):

* ``features.txt`` — genomic feature (allele) rows: id, SO type, symbol,
  human-readable type, mutagen, and — for transgenic insertions — the
  construct's id and name. NOT one row per allele: ~1.7k alleles repeat,
  either identically (differing only in a trailing reagent column) or once
  per construct (a co-injected line like gz13Tg is ONE insertion event
  carrying TWO constructs), so rows are aggregated by allele id.
* ``features-affected-genes.txt`` — feature→gene rows. Only the
  ``is allele of`` relationship is indexed; transgenic insertions have no
  such rows (their gene-ish search surface is the construct name instead).
* ``wildtypes_fish.txt`` — the wild-type lines with their fish/genotype ids.

The whole index lives in memory (~84k alleles, a few tens of MB) and is built
lazily on first use, cached per data directory. Searches are linear scans —
tens of milliseconds, fine for autocomplete; revisit only if it ever isn't.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from pathlib import Path

from linkml_runtime import SchemaView

from zapp_atlas.schema.constraints import SCHEMA_PATH
from zapp_atlas.schema.pydantic_crud import SequenceAlterationTypeEnum

_REQUIRED_FILES = ("features.txt", "features-affected-genes.txt", "wildtypes_fish.txt")
_SO_TRANSGENIC_INSERTION = "SO:0001218"
_AFFECTED_GENE_RELATIONSHIP = "is allele of"


class ZfinDataUnavailable(RuntimeError):
    """The ZFIN download files are not present in the configured data dir."""


def _curie(zdb_id: str) -> str:
    return f"ZFIN:{zdb_id}"


@cache
def _so_to_alteration_type() -> dict[str, SequenceAlterationTypeEnum]:
    """SO term → SequenceAlterationTypeEnum, read from the schema's meanings.

    The YAML stays the single source of truth: a new permissible value with a
    ``meaning`` becomes resolvable here without touching this module.
    """
    view = SchemaView(str(SCHEMA_PATH))
    enum = view.get_enum("SequenceAlterationTypeEnum")
    return {
        pv.meaning: SequenceAlterationTypeEnum(name)
        for name, pv in enum.permissible_values.items()
        if pv.meaning
    }


@dataclass(frozen=True)
class AffectedGene:
    gene_symbol: str
    gene_id: str  # CURIE (ZFIN:ZDB-GENE-…)


@dataclass(frozen=True)
class Construct:
    construct_id: str  # CURIE (ZFIN:ZDB-TGCONSTRCT-…)
    construct_name: str


@dataclass(frozen=True)
class AlleleRecord:
    allele_symbol: str
    allele_id: str  # CURIE (ZFIN:ZDB-ALT-…)
    is_transgenic: bool
    alteration_type: SequenceAlterationTypeEnum | None
    alteration_label: str  # ZFIN's human-readable type, always present
    mutagen: str | None
    constructs: tuple[Construct, ...]  # usually 0 or 1; >1 for co-injected lines
    affected_genes: tuple[AffectedGene, ...]


@dataclass(frozen=True)
class WildtypeLine:
    name: str
    abbreviation: str
    fish_id: str  # CURIE (ZFIN:ZDB-FISH-…)
    genotype_id: str  # CURIE (ZFIN:ZDB-GENO-…)


@dataclass(frozen=True)
class _SearchRow:
    """An allele plus its precomputed lowercase search surface."""

    record: AlleleRecord
    symbol: str
    genes: tuple[str, ...]
    construct: str


class ZfinIndex:
    def __init__(self, alleles: list[AlleleRecord], wildtypes: list[WildtypeLine]):
        self.wildtypes = wildtypes
        self.allele_count = len(alleles)
        self._rows = [
            _SearchRow(
                record=rec,
                symbol=rec.allele_symbol.lower(),
                genes=tuple(g.gene_symbol.lower() for g in rec.affected_genes),
                construct=" ".join(c.construct_name for c in rec.constructs).lower(),
            )
            for rec in alleles
        ]

    def search_alleles(self, query: str, limit: int) -> tuple[int, list[AlleleRecord]]:
        """Ranked substring search; returns (total matches, top ``limit``)."""
        q = query.strip().lower()
        matches: list[tuple[int, str, AlleleRecord]] = []
        for row in self._rows:
            rank = _rank(row, q)
            if rank is not None:
                matches.append((rank, row.symbol, row.record))
        matches.sort(key=lambda m: (m[0], m[1]))
        return len(matches), [record for _, _, record in matches[:limit]]


def _rank(row: _SearchRow, q: str) -> int | None:
    """Lower is better; None means no match. Exact beats prefix beats substring,
    and the allele symbol beats the gene beats the construct at each strength."""
    if row.symbol == q:
        return 0
    if q in row.genes:
        return 1
    if row.symbol.startswith(q):
        return 2
    if any(g.startswith(q) for g in row.genes):
        return 3
    if row.construct and q in row.construct:
        return 4
    if q in row.symbol:
        return 5
    if any(q in g for g in row.genes):
        return 6
    return None


def _parse_features(path: Path, affected: dict[str, list[AffectedGene]]) -> list[AlleleRecord]:
    so_map = _so_to_alteration_type()
    # Aggregated by allele id, insertion-ordered; repeated rows merge into one
    # record, accumulating any distinct constructs.
    partial: dict[str, dict] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 5:
                continue
            zdb_id, so_id, symbol = cols[0], cols[1], cols[2]
            if not zdb_id.startswith("ZDB-ALT-") or not symbol:
                continue
            construct_zdb = cols[7] if len(cols) > 7 and cols[7] else None
            construct_name = cols[8] if len(cols) > 8 and cols[8] else None
            mutagen = cols[5] if len(cols) > 5 and cols[5] not in ("", "not specified") else None

            entry = partial.setdefault(
                zdb_id,
                {
                    "allele_symbol": symbol,
                    "so_id": so_id,
                    "alteration_label": cols[4] or "Unknown",
                    "mutagen": mutagen,
                    "constructs": [],
                },
            )
            if entry["mutagen"] is None:
                entry["mutagen"] = mutagen
            if construct_zdb and construct_name:
                construct = Construct(_curie(construct_zdb), construct_name)
                if construct not in entry["constructs"]:
                    entry["constructs"].append(construct)

    return [
        AlleleRecord(
            allele_symbol=entry["allele_symbol"],
            allele_id=_curie(zdb_id),
            is_transgenic=entry["so_id"] == _SO_TRANSGENIC_INSERTION or bool(entry["constructs"]),
            alteration_type=so_map.get(entry["so_id"]),
            alteration_label=entry["alteration_label"],
            mutagen=entry["mutagen"],
            constructs=tuple(entry["constructs"]),
            affected_genes=tuple(affected.get(zdb_id, ())),
        )
        for zdb_id, entry in partial.items()
    ]


def _parse_affected_genes(path: Path) -> dict[str, list[AffectedGene]]:
    affected: dict[str, list[AffectedGene]] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 7 or cols[6] != _AFFECTED_GENE_RELATIONSHIP:
                continue
            zdb_id, gene_symbol, gene_id = cols[0], cols[3], cols[4]
            if not gene_symbol or not gene_id:
                continue
            genes = affected.setdefault(zdb_id, [])
            if all(g.gene_id != _curie(gene_id) for g in genes):
                genes.append(AffectedGene(gene_symbol=gene_symbol, gene_id=_curie(gene_id)))
    return affected


def _parse_wildtypes(path: Path) -> list[WildtypeLine]:
    lines: list[WildtypeLine] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 4 or not cols[0].startswith("ZDB-FISH-"):
                continue
            lines.append(
                WildtypeLine(
                    name=cols[1],
                    abbreviation=cols[2] or cols[1],
                    fish_id=_curie(cols[0]),
                    genotype_id=_curie(cols[3]),
                )
            )
    lines.sort(key=lambda w: w.name.lower())
    return lines


_INDEXES: dict[Path, ZfinIndex] = {}


def get_index(data_dir: Path) -> ZfinIndex:
    """The (cached) in-memory index for ``data_dir``.

    Raises ZfinDataUnavailable when the download files are absent, so callers
    can turn it into a 503 that says how to fetch them.
    """
    key = data_dir.resolve()
    index = _INDEXES.get(key)
    if index is not None:
        return index

    missing = [name for name in _REQUIRED_FILES if not (key / name).is_file()]
    if missing:
        raise ZfinDataUnavailable(
            f"ZFIN reference data not available: missing {', '.join(missing)} "
            f"in {key}. Run `just fetch-zfin` (or set ZAPP_ZFIN_DATA_DIR)."
        )

    affected = _parse_affected_genes(key / "features-affected-genes.txt")
    index = ZfinIndex(
        alleles=_parse_features(key / "features.txt", affected),
        wildtypes=_parse_wildtypes(key / "wildtypes_fish.txt"),
    )
    _INDEXES[key] = index
    return index
