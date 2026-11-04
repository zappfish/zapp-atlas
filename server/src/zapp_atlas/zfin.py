"""ZFIN's registry of fish lines, from the extdata bundle's zfin.db.

The database is built offline by ``extdata/scripts/zfin_db.py`` from ZFIN's
bulk downloads (which documents its tables and their sources) and holds the
registered alleles, genotypes, fish, reagents and wild-type lines. This module
is the read side: typed lookups by id, allele autocomplete, the list of
wild-type lines, and ``resolve``, which finds the registered genotype and
fish a curator's description of a fish corresponds to. Ids are CURIEs
(``ZFIN:ZDB-ALT-...``) throughout.

Like ``labels.py``, it opens the file read-only and immutable once, at
startup, and shares the connection across request threads. Without a bundle
``available`` is False and every lookup raises ``ZfinUnavailable``; routes
turn that into a 503 that says how to build it.

Routes get the app's instance with the ``ZfinData`` dependency.
"""

import logging
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from fastapi import Depends, Request

logger = logging.getLogger(__name__)

# Characters FTS5's unicode61 tokenizer treats as separators, near enough: a
# query is split on them, and each piece becomes a prefix term.
_TOKEN_SPLIT = re.compile(r"[^\w]+")
_FTS_CANDIDATES = 2000


class ZfinUnavailable(RuntimeError):
    """zfin.db is not installed."""


@dataclass(frozen=True)
class Gene:
    gene_id: str
    symbol: str


@dataclass(frozen=True)
class Construct:
    construct_id: str
    name: str


@dataclass(frozen=True)
class Wildtype:
    fish_id: str
    genotype_id: str
    name: str
    abbreviation: str


@dataclass(frozen=True)
class Background:
    background_id: str
    name: str


@dataclass(frozen=True)
class Allele:
    allele_id: str
    symbol: str
    name: str
    so_id: str | None
    type_label: str
    mutagen: str | None
    is_transgenic: bool
    genes: tuple[Gene, ...]
    constructs: tuple[Construct, ...]


@dataclass(frozen=True)
class GenotypeAllele:
    allele_id: str
    symbol: str
    zygosity: str
    mother_zygosity: str | None
    father_zygosity: str | None


@dataclass(frozen=True)
class GenotypeRef:
    genotype_id: str
    name: str
    name_plain: str


@dataclass(frozen=True)
class Genotype:
    genotype_id: str
    name: str
    name_plain: str
    unique_name: str | None
    alleles: tuple[GenotypeAllele, ...]
    backgrounds: tuple[Background, ...]


@dataclass(frozen=True)
class Reagent:
    reagent_id: str
    symbol: str
    kind: str
    genes: tuple[Gene, ...]


@dataclass(frozen=True)
class Fish:
    fish_id: str
    name: str
    name_plain: str
    genotype: GenotypeRef
    backgrounds: tuple[Background, ...]
    reagents: tuple[Reagent, ...]


@dataclass(frozen=True)
class FishRef:
    fish_id: str
    name: str
    name_plain: str


@dataclass(frozen=True)
class Candidate:
    """A registered genotype matching a description, with the fish of that
    genotype carrying exactly the described reagents (usually one)."""

    genotype: GenotypeRef
    backgrounds: tuple[Background, ...]
    fish: tuple[FishRef, ...]


@dataclass(frozen=True)
class Resolution:
    candidates: tuple[Candidate, ...]

    @property
    def genotype(self) -> GenotypeRef | None:
        """The one matching genotype, when the description is unambiguous."""
        return self.candidates[0].genotype if len(self.candidates) == 1 else None

    @property
    def fish(self) -> FishRef | None:
        """The one registered fish for that genotype with these reagents."""
        if len(self.candidates) == 1 and len(self.candidates[0].fish) == 1:
            return self.candidates[0].fish[0]
        return None


@dataclass(frozen=True)
class _Candidate:
    allele_id: str
    symbol: str
    name: str
    genes: str
    constructs: str


def _rank(c: _Candidate, q: str, tokens: list[str]) -> int:
    """Lower is better. The allele's own symbol beats its gene beats its
    construct, and at each an exact hit beats a prefix beats a substring."""
    genes = c.genes.split()
    if c.symbol == q:
        return 0
    if q in genes:
        return 1
    if c.symbol.startswith(q):
        return 2
    if any(g.startswith(q) for g in genes):
        return 3
    if q in c.constructs:
        return 4
    if q in c.symbol:
        return 5
    if q in c.genes:
        return 6
    if q in c.name:
        return 7
    # Every token matched the start of some word (that is what FTS found),
    # just not as one contiguous string: "mpeg1 yfp" against "Tg(mpeg1:YFP)".
    return 8 if len(tokens) > 1 else 9


class Zfin:
    def __init__(self, db_path: Path):
        self._db: sqlite3.Connection | None = None
        if not db_path.is_file():
            logger.warning(
                "ZFIN data not found at %s; /api/zfin will answer 503. "
                "Build the extdata bundle with `just extdata`.",
                db_path,
            )
            return
        self._db = sqlite3.connect(
            f"{db_path.resolve().as_uri()}?mode=ro&immutable=1",
            uri=True,
            check_same_thread=False,
        )
        self._db.row_factory = sqlite3.Row

    @property
    def available(self) -> bool:
        return self._db is not None

    @property
    def db(self) -> sqlite3.Connection:
        if self._db is None:
            raise ZfinUnavailable(
                "ZFIN reference data is not installed: the extdata bundle has no zfin.db. "
                "Build it with `just extdata`."
            )
        return self._db

    # -- meta ---------------------------------------------------------------

    def meta(self) -> dict[str, str]:
        return {row["key"]: row["value"] for row in self.db.execute("SELECT key, value FROM meta")}

    # -- wild types -----------------------------------------------------------

    def wildtypes(self) -> list[Wildtype]:
        return [
            Wildtype(**row)
            for row in self.db.execute(
                "SELECT fish_id, genotype_id, name, abbreviation FROM wildtype ORDER BY name"
            )
        ]

    # -- alleles --------------------------------------------------------------

    def allele(self, allele_id: str) -> Allele | None:
        row = self.db.execute(
            "SELECT allele_id, symbol, name, so_id, type_label, mutagen, is_transgenic "
            "FROM allele WHERE allele_id = ?",
            (allele_id,),
        ).fetchone()
        return self._allele(row) if row else None

    def _allele(self, row: sqlite3.Row) -> Allele:
        return Allele(
            **{
                k: row[k] for k in ("allele_id", "symbol", "name", "so_id", "type_label", "mutagen")
            },
            is_transgenic=bool(row["is_transgenic"]),
            genes=self._allele_genes(row["allele_id"]),
            constructs=tuple(
                Construct(r["construct_id"], r["construct_name"])
                for r in self.db.execute(
                    "SELECT construct_id, construct_name FROM allele_construct "
                    "WHERE allele_id = ? ORDER BY construct_name",
                    (row["allele_id"],),
                )
            ),
        )

    def _allele_genes(self, allele_id: str) -> tuple[Gene, ...]:
        return tuple(
            Gene(r["gene_id"], r["gene_symbol"])
            for r in self.db.execute(
                "SELECT gene_id, gene_symbol FROM allele_gene WHERE allele_id = ? ORDER BY gene_symbol",
                (allele_id,),
            )
        )

    def search_alleles(self, query: str, limit: int) -> tuple[int, list[Allele]]:
        """Alleles matching ``query`` by symbol, gene symbol, construct name or
        full name, best first: ``(total matches, the first limit of them)``."""
        q = query.strip().lower()
        tokens = [t for t in _TOKEN_SPLIT.split(q) if t]
        if not tokens:
            return 0, []

        # Word-prefix matches from the FTS index, then whole-symbol substring
        # matches the tokenizer cannot see ("h111" in "fh111").
        candidates: dict[str, _Candidate] = {}
        match = " ".join(f'"{t}"*' for t in tokens)
        for row in self.db.execute(
            "SELECT allele_id, symbol, name, genes, constructs FROM allele_fts "
            "WHERE allele_fts MATCH ? LIMIT ?",
            (match, _FTS_CANDIDATES),
        ):
            candidates[row["allele_id"]] = _candidate(row)
        if len(tokens) == 1:
            like = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
            for row in self.db.execute(
                "SELECT allele_id, symbol, name, '' AS genes, '' AS constructs FROM allele "
                "WHERE symbol LIKE ? ESCAPE '\\'",
                (like,),
            ):
                candidates.setdefault(row["allele_id"], _candidate(row))

        ranked = sorted(
            ((_rank(c, q, tokens), c.symbol, c.allele_id) for c in candidates.values()),
        )
        found = [self.allele(allele_id) for _, _, allele_id in ranked[:limit]]
        return len(ranked), [a for a in found if a is not None]

    # -- genotypes ------------------------------------------------------------

    def genotype(self, genotype_id: str) -> Genotype | None:
        row = self.db.execute(
            "SELECT genotype_id, name, name_plain, unique_name FROM genotype WHERE genotype_id = ?",
            (genotype_id,),
        ).fetchone()
        if row is None:
            return None
        return Genotype(
            **row,
            alleles=tuple(
                GenotypeAllele(
                    allele_id=r["allele_id"],
                    symbol=r["allele_symbol"],
                    zygosity=r["zygosity"],
                    mother_zygosity=r["mother_zygosity"],
                    father_zygosity=r["father_zygosity"],
                )
                for r in self.db.execute(
                    "SELECT allele_id, allele_symbol, zygosity, mother_zygosity, father_zygosity "
                    "FROM genotype_allele WHERE genotype_id = ? ORDER BY allele_symbol",
                    (genotype_id,),
                )
            ),
            backgrounds=self._backgrounds("genotype_background", "genotype_id", genotype_id),
        )

    # -- fish -----------------------------------------------------------------

    def fish(self, fish_id: str) -> Fish | None:
        row = self.db.execute(
            "SELECT f.fish_id, f.name, f.name_plain, g.genotype_id, "
            "g.name AS genotype_name, g.name_plain AS genotype_name_plain "
            "FROM fish f JOIN genotype g USING (genotype_id) WHERE f.fish_id = ?",
            (fish_id,),
        ).fetchone()
        if row is None:
            return None
        return Fish(
            fish_id=row["fish_id"],
            name=row["name"],
            name_plain=row["name_plain"],
            genotype=GenotypeRef(
                row["genotype_id"], row["genotype_name"], row["genotype_name_plain"]
            ),
            backgrounds=self._backgrounds("fish_background", "fish_id", fish_id),
            reagents=tuple(
                Reagent(
                    reagent_id=r["reagent_id"],
                    symbol=r["symbol"],
                    kind=r["kind"],
                    genes=tuple(
                        Gene(g["gene_id"], g["gene_symbol"])
                        for g in self.db.execute(
                            "SELECT gene_id, gene_symbol FROM reagent_gene "
                            "WHERE reagent_id = ? ORDER BY gene_symbol",
                            (r["reagent_id"],),
                        )
                    ),
                )
                for r in self.db.execute(
                    "SELECT r.reagent_id, r.symbol, r.kind FROM fish_reagent fr "
                    "JOIN reagent r USING (reagent_id) WHERE fr.fish_id = ? ORDER BY r.symbol",
                    (fish_id,),
                )
            ),
        )

    # -- resolution -----------------------------------------------------------

    def resolve(
        self,
        alleles: dict[str, str],
        background_id: str | None,
        reagents: set[str],
    ) -> Resolution:
        """The registered genotypes carrying exactly ``alleles`` (allele id ->
        zygosity), and for each the fish injected with exactly ``reagents``.

        Matching is by identity, as ZFIN's own records are keyed: the same
        alleles at a different zygosity are a different genotype, and
        "unknown" is a zygosity in its own right, not a wildcard. With no
        alleles the description is a wild-type line: ``background_id`` is the
        genotype.

        ZFIN records a background for only a third of its genotypes. When one
        is given, genotypes on a *different* background are excluded; those on
        none are kept unless some candidate is on the given one, which then
        wins. Several genotypes can still match (ZFIN registers the same
        alleles on backgrounds it did not record), so the caller gets all of
        them and ``Resolution.genotype`` is set only when there is one.
        """
        if alleles:
            placeholders = ", ".join("(?, ?)" for _ in alleles)
            genotype_ids = [
                row["genotype_id"]
                for row in self.db.execute(
                    f"""
                    SELECT genotype_id FROM genotype_allele
                    WHERE (allele_id, zygosity) IN (VALUES {placeholders})
                    GROUP BY genotype_id
                    HAVING count(*) = ? AND count(*) = (
                        SELECT count(*) FROM genotype_allele ga
                        WHERE ga.genotype_id = genotype_allele.genotype_id)
                    """,
                    [*(v for pair in alleles.items() for v in pair), len(alleles)],
                )
            ]
        elif background_id:
            genotype_ids = [
                row["genotype_id"]
                for row in self.db.execute(
                    "SELECT genotype_id FROM wildtype WHERE genotype_id = ?", (background_id,)
                )
            ]
        else:
            genotype_ids = []

        candidates = []
        for genotype_id in genotype_ids:
            backgrounds = self._backgrounds("genotype_background", "genotype_id", genotype_id)
            recorded_on = {b.background_id for b in backgrounds}
            if background_id and alleles and recorded_on and background_id not in recorded_on:
                continue
            row = self.db.execute(
                "SELECT genotype_id, name, name_plain FROM genotype WHERE genotype_id = ?",
                (genotype_id,),
            ).fetchone()
            candidates.append(
                Candidate(
                    genotype=GenotypeRef(**row),
                    backgrounds=backgrounds,
                    fish=self._fish_with_reagents(genotype_id, reagents),
                )
            )
        if background_id and alleles:
            on_background = [
                c for c in candidates if background_id in {b.background_id for b in c.backgrounds}
            ]
            if on_background:
                candidates = on_background
        candidates.sort(key=lambda c: c.genotype.genotype_id)
        return Resolution(tuple(candidates))

    def _fish_with_reagents(self, genotype_id: str, reagents: set[str]) -> tuple[FishRef, ...]:
        found = []
        for row in self.db.execute(
            "SELECT fish_id, name, name_plain FROM fish WHERE genotype_id = ? ORDER BY fish_id",
            (genotype_id,),
        ):
            carried = {
                r["reagent_id"]
                for r in self.db.execute(
                    "SELECT reagent_id FROM fish_reagent WHERE fish_id = ?", (row["fish_id"],)
                )
            }
            if carried == reagents:
                found.append(FishRef(**row))
        return tuple(found)

    def _backgrounds(self, table: str, column: str, key: str) -> tuple[Background, ...]:
        # table/column name the two callers in this module, not request data.
        return tuple(
            Background(r["background_id"], r["name"])
            for r in self.db.execute(
                f"SELECT b.background_id, b.name FROM {table} t "
                f"JOIN background b USING (background_id) WHERE t.{column} = ? ORDER BY b.name",
                (key,),
            )
        )


def _candidate(row: sqlite3.Row) -> _Candidate:
    return _Candidate(
        allele_id=row["allele_id"],
        symbol=row["symbol"].lower(),
        name=row["name"].lower(),
        genes=(row["genes"] or "").lower(),
        constructs=(row["constructs"] or "").lower(),
    )


def get_zfin(request: Request) -> Zfin:
    return request.app.state.zfin


ZfinData = Annotated[Zfin, Depends(get_zfin)]
