"""zapp_atlas.zfin against a database built from tests/zfin_fixture."""

import pytest

from zapp_atlas.zfin import Zfin, ZfinUnavailable

FH111 = "ZFIN:ZDB-ALT-160602-14"
W200TG = "ZFIN:ZDB-ALT-130130-3"
GZ13TG = "ZFIN:ZDB-ALT-070117-1"
C1033 = "ZFIN:ZDB-ALT-000215-12"
AB = "ZFIN:ZDB-GENO-960809-7"
TU = "ZFIN:ZDB-GENO-990623-3"


@pytest.fixture(scope="module")
def zfin(zfin_db) -> Zfin:
    return Zfin(zfin_db)


def test_without_a_database_every_lookup_is_unavailable(tmp_path):
    zfin = Zfin(tmp_path / "missing.db")
    assert not zfin.available
    with pytest.raises(ZfinUnavailable, match="just extdata"):
        zfin.wildtypes()


def test_meta_records_the_snapshot_and_counts(zfin):
    meta = zfin.meta()
    assert meta["zfin_date"] == "2026.11.01"
    assert meta["allele_count"] == "7"
    assert meta["wildtype_count"] == "2"


def test_wildtypes_are_sorted_by_name(zfin):
    assert [w.name for w in zfin.wildtypes()] == ["AB", "TU"]
    ab = zfin.wildtypes()[0]
    assert (ab.fish_id, ab.genotype_id) == ("ZFIN:ZDB-FISH-150901-27842", AB)


def test_allele_aggregates_its_constructs(zfin):
    allele = zfin.allele(GZ13TG)
    assert allele.is_transgenic
    assert [c.name for c in allele.constructs] == ["Tg(fli1a:EGFP)", "Tg(gata1:DsRed)"]
    assert allele.genes == ()


def test_allele_genes_come_from_is_allele_of_rows_only(zfin):
    assert [g.symbol for g in zfin.allele(FH111).genes] == ["snapc1b"]
    assert zfin.allele(C1033).genes == ()  # its row says "markers missing"
    assert zfin.allele(C1033).name == "Df(Chr03)c1033"


def test_allele_gene_recorded_only_on_a_fish_is_kept(zfin):
    assert [g.symbol for g in zfin.allele(W200TG).genes] == ["mpeg1"]


def test_allele_without_so_id(zfin):
    allele = zfin.allele("ZFIN:ZDB-ALT-200101-1")
    assert allele.so_id is None
    assert allele.mutagen is None
    assert allele.type_label == "Allele with one mnv"


def test_unknown_ids_are_none(zfin):
    assert zfin.allele("ZFIN:ZDB-ALT-000000-0") is None
    assert zfin.genotype("ZFIN:ZDB-GENO-000000-0") is None
    assert zfin.fish("ZFIN:ZDB-FISH-000000-0") is None


def test_search_ranks_symbol_over_gene_over_construct(zfin):
    total, results = zfin.search_alleles("fh111", 10)
    assert total == 1
    assert results[0].symbol == "fh111"

    # The gene's own allele first, then the allele whose construct mentions it.
    total, results = zfin.search_alleles("fgf8a", 10)
    assert [a.symbol for a in results] == ["ti282a"]

    _, results = zfin.search_alleles("mpeg1:YFP", 10)
    assert [a.symbol for a in results] == ["w200Tg"]


def test_search_finds_substrings_inside_a_symbol(zfin):
    _, results = zfin.search_alleles("h111", 10)
    assert [a.symbol for a in results] == ["fh111"]


def test_search_is_case_insensitive_and_limited(zfin):
    total, results = zfin.search_alleles("TG", 1)
    assert total == 2  # w200Tg and gz13Tg
    assert len(results) == 1


def test_search_with_nothing_to_match(zfin):
    assert zfin.search_alleles("zzzz", 10) == (0, [])
    assert zfin.search_alleles("  ", 10) == (0, [])


def test_genotype_carries_alleles_with_zygosity_and_background(zfin):
    genotype = zfin.genotype("ZFIN:ZDB-GENO-160602-1")
    assert genotype.name == "snapc1b<sup>fh111/+</sup>"
    assert genotype.name_plain == "snapc1bfh111/+"
    assert genotype.unique_name == "fh111[1,1,2]AB"
    (allele,) = genotype.alleles
    assert (allele.symbol, allele.zygosity) == ("fh111", "heterozygous")
    assert (allele.mother_zygosity, allele.father_zygosity) == ("heterozygous", "homozygous")
    assert [b.name for b in genotype.backgrounds] == ["AB", "TU"]


def test_genotype_with_repeated_construct_rows_has_one_allele(zfin):
    genotype = zfin.genotype("ZFIN:ZDB-GENO-070117-1")
    assert [a.symbol for a in genotype.alleles] == ["gz13Tg"]


def test_two_allele_genotype(zfin):
    genotype = zfin.genotype("ZFIN:ZDB-GENO-170101-1")
    assert [(a.symbol, a.zygosity) for a in genotype.alleles] == [
        ("fh111", "homozygous"),
        ("w200Tg", "heterozygous"),
    ]
    assert [a.mother_zygosity for a in genotype.alleles] == ["unknown", "unknown"]


def test_unparseable_unique_name_leaves_parental_zygosity_unknown(zfin):
    (allele,) = zfin.genotype("ZFIN:ZDB-GENO-180101-1").alleles
    assert allele.zygosity == "homozygous"
    assert allele.mother_zygosity is None
    assert allele.father_zygosity is None


def test_wildtype_line_is_a_genotype_and_a_fish(zfin):
    assert zfin.genotype(AB).alleles == ()
    assert zfin.genotype(AB).unique_name is None
    fish = zfin.fish("ZFIN:ZDB-FISH-150901-27842")
    assert fish.genotype.genotype_id == AB
    assert fish.reagents == ()


def test_fish_on_two_backgrounds(zfin):
    fish = zfin.fish("ZFIN:ZDB-FISH-160602-1")
    assert [b.background_id for b in fish.backgrounds] == [AB, TU]
    assert fish.genotype.name_plain == "snapc1bfh111/+"


def test_fish_with_a_reagent_hitting_two_genes(zfin):
    fish = zfin.fish("ZFIN:ZDB-FISH-160602-2")
    assert fish.name_plain == "snapc1bfh111/+ + MO1-fgf8a"
    (reagent,) = fish.reagents
    assert (reagent.symbol, reagent.kind) == ("MO1-fgf8a", "morpholino")
    assert [g.symbol for g in reagent.genes] == ["fgf8a", "fgf8b"]


# -- resolve ------------------------------------------------------------------

TI282A = "ZFIN:ZDB-ALT-980203-1091"
MO1_FGF8A = "ZFIN:ZDB-MRPHLNO-040101-1"


def test_resolve_alleles_on_a_background_to_one_genotype_and_fish(zfin):
    found = zfin.resolve({FH111: "heterozygous"}, AB, set())
    assert found.genotype.genotype_id == "ZFIN:ZDB-GENO-160602-1"
    assert found.fish.fish_id == "ZFIN:ZDB-FISH-160602-1"
    assert [b.name for b in found.candidates[0].backgrounds] == ["AB", "TU"]


def test_resolve_matches_zygosity_exactly(zfin):
    # fh111 is registered heterozygous (alone) and homozygous (with w200Tg);
    # "unknown" is a value, not a wildcard.
    assert zfin.resolve({FH111: "homozygous"}, AB, set()).candidates == ()
    assert zfin.resolve({FH111: "unknown"}, AB, set()).candidates == ()


def test_resolve_needs_the_whole_allele_set(zfin):
    found = zfin.resolve({FH111: "homozygous", W200TG: "heterozygous"}, None, set())
    assert found.genotype.genotype_id == "ZFIN:ZDB-GENO-170101-1"
    # A subset of a genotype's alleles is not that genotype.
    assert zfin.resolve({W200TG: "heterozygous"}, None, set()).candidates == ()


def test_resolve_reagents_pick_the_fish(zfin):
    plain = zfin.resolve({FH111: "heterozygous"}, AB, set())
    injected = zfin.resolve({FH111: "heterozygous"}, AB, {MO1_FGF8A})
    assert plain.genotype == injected.genotype
    assert plain.fish.fish_id == "ZFIN:ZDB-FISH-160602-1"
    assert injected.fish.fish_id == "ZFIN:ZDB-FISH-160602-2"
    # A reagent combination ZFIN has no fish for: the genotype still resolves.
    unregistered = zfin.resolve({FH111: "heterozygous"}, AB, {MO1_FGF8A, "ZFIN:ZDB-CRISPR-1-1"})
    assert unregistered.genotype is not None
    assert unregistered.fish is None


def test_resolve_a_different_background_is_a_different_genotype(zfin):
    # ti282a/ti282a is registered on TU only.
    assert zfin.resolve({TI282A: "homozygous"}, TU, set()).genotype is not None
    assert zfin.resolve({TI282A: "homozygous"}, AB, set()).candidates == ()


def test_resolve_without_a_background_accepts_any(zfin):
    found = zfin.resolve({TI282A: "homozygous"}, None, set())
    assert found.genotype.genotype_id == "ZFIN:ZDB-GENO-180101-1"


def test_resolve_a_genotype_with_no_recorded_background_is_kept(zfin):
    # w200Tg's genotype has no background rows, so any stated background is compatible.
    found = zfin.resolve({W200TG: "unknown"}, TU, set())
    assert found.genotype.genotype_id == "ZFIN:ZDB-GENO-130130-1"
    assert found.candidates[0].backgrounds == ()


def test_resolve_no_alleles_is_the_wild_type_line(zfin):
    found = zfin.resolve({}, AB, set())
    assert found.genotype.genotype_id == AB
    assert found.fish.fish_id == "ZFIN:ZDB-FISH-150901-27842"
    assert zfin.resolve({}, "ZFIN:ZDB-GENO-000000-0", set()).candidates == ()
    assert zfin.resolve({}, None, set()).candidates == ()
