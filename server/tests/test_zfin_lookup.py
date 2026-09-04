"""/api/zfin lookups against a miniature ZFIN download set.

The fixture files mirror the real download formats row-for-row (tab-separated,
no header): features.txt column 8/9 carry the construct id/name for transgenic
insertions, and features-affected-genes.txt rows only count when their
relationship column says ``is allele of``.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from zapp_atlas.main import create_app
from zapp_atlas.settings import AppSettings

# (id, SO type, symbol, symbol, type label, mutagen, mutagee, construct id,
#  construct name, construct SO, unused) — as in the real features.txt.
FEATURE_ROWS = [
    (
        "ZDB-ALT-160602-14",
        "SO:1000008",
        "fh111",
        "fh111",
        "Allele with one point mutation",
        "ENU",
        "not specified",
        "",
        "",
        "",
        "",
    ),
    (
        "ZDB-ALT-980203-1091",
        "SO:1000008",
        "ti282a",
        "ti282a",
        "Allele with one point mutation",
        "ENU",
        "adult males",
        "",
        "",
        "",
        "",
    ),
    (
        "ZDB-ALT-130130-3",
        "SO:0001218",
        "w200Tg",
        "w200Tg",
        "Transgenic Insertion",
        "DNA",
        "embryos",
        "ZDB-TGCONSTRCT-130130-3",
        "Tg(mpeg1:YFP)",
        "SO:0000637",
        "",
    ),
    (
        "ZDB-ALT-011017-4",
        "SO:0001059",
        "a101",
        "a101",
        "Unknown",
        "not specified",
        "not specified",
        "",
        "",
        "",
        "",
    ),
    (
        "ZDB-ALT-200101-1",
        "SO:0001023",
        "fh900",
        "fh900",
        "Allele",
        "not specified",
        "not specified",
        "",
        "",
        "",
        "",
    ),
    (
        "ZDB-ALT-200101-2",
        "SO:0000159",
        "fh901",
        "fh901",
        "Allele with one deleted sequence",
        "CRISPR",
        "embryos",
        "",
        "",
        "",
        "",
    ),
    # A co-injected line: one allele id, one row per construct (real pattern,
    # cf. gz13Tg). Must aggregate to ONE record with BOTH constructs.
    (
        "ZDB-ALT-090312-1",
        "SO:0001218",
        "gz13Tg",
        "gz13Tg",
        "Transgenic Insertion",
        "DNA",
        "embryos",
        "ZDB-TGCONSTRCT-090312-1",
        "Tg2(krt4:GFP)",
        "SO:0000637",
        "",
    ),
    (
        "ZDB-ALT-090312-1",
        "SO:0001218",
        "gz13Tg",
        "gz13Tg",
        "Transgenic Insertion",
        "DNA",
        "embryos",
        "ZDB-TGCONSTRCT-140429-7",
        "Tg2(mylpfa:RFP)",
        "SO:0000637",
        "",
    ),
    # The same row repeated identically (real pattern: rows that differ only
    # in a trailing reagent column). Must collapse to one record.
    (
        "ZDB-ALT-240826-1",
        "SO:0001218",
        "tud121Tg",
        "tud121Tg",
        "Transgenic Insertion",
        "DNA",
        "embryos",
        "ZDB-TGCONSTRCT-180530-1",
        "Tg(EGFP)",
        "SO:0000637",
        "",
    ),
    (
        "ZDB-ALT-240826-1",
        "SO:0001218",
        "tud121Tg",
        "tud121Tg",
        "Transgenic Insertion",
        "DNA",
        "embryos",
        "ZDB-TGCONSTRCT-180530-1",
        "Tg(EGFP)",
        "SO:0000637",
        "",
    ),
]

DISTINCT_ALLELES = 8

# (id, SO type, symbol, gene symbol, gene id, gene SO, relationship)
AFFECTED_ROWS = [
    (
        "ZDB-ALT-160602-14",
        "SO:1000008",
        "fh111",
        "snapc1b",
        "ZDB-GENE-040426-716",
        "SO:0001217",
        "is allele of",
    ),
    (
        "ZDB-ALT-980203-1091",
        "SO:1000008",
        "ti282a",
        "fgf8a",
        "ZDB-GENE-990415-72",
        "SO:0001217",
        "is allele of",
    ),
    (
        "ZDB-ALT-011017-4",
        "SO:0001059",
        "a101",
        "lze",
        "ZDB-GENE-070117-60",
        "SO:0001217",
        "is allele of",
    ),
    # Non-"is allele of" relationships exist in the real file and must be skipped.
    (
        "ZDB-ALT-200101-2",
        "SO:0000159",
        "fh901",
        "wrongene",
        "ZDB-GENE-000000-1",
        "SO:0001217",
        "markers missing",
    ),
]

# (fish id, name, abbreviation, genotype id)
WILDTYPE_ROWS = [
    ("ZDB-FISH-150901-29105", "TU", "TU", "ZDB-GENO-990623-3"),
    ("ZDB-FISH-150901-27842", "AB", "AB", "ZDB-GENO-960809-7"),
    ("ZDB-FISH-150901-28277", "WIK", "WIK", "ZDB-GENO-010531-2"),
]


def _write_downloads(data_dir):
    rows = {
        "features.txt": FEATURE_ROWS,
        "features-affected-genes.txt": AFFECTED_ROWS,
        "wildtypes_fish.txt": WILDTYPE_ROWS,
    }
    for name, table in rows.items():
        text = "".join("\t".join(row) + "\n" for row in table)
        (data_dir / name).write_text(text, encoding="utf-8")


def _make_client(tmp_path, zfin_data_dir) -> TestClient:
    settings = AppSettings(
        skip_seed=True,
        upload_dir=tmp_path,
        db_path=tmp_path / "test.db",
        zfin_data_dir=zfin_data_dir,
        _env_file=None,
    )
    return TestClient(create_app(settings))


@pytest.fixture
def zfin_client(tmp_path) -> TestClient:
    data_dir = tmp_path / "zfin"
    data_dir.mkdir()
    _write_downloads(data_dir)
    return _make_client(tmp_path, data_dir)


def test_exact_symbol_fills_the_whole_card(zfin_client):
    body = zfin_client.get("/api/zfin/alleles", params={"q": "fh111"}).json()
    assert body["indexed_alleles"] == DISTINCT_ALLELES
    hit = body["results"][0]
    assert hit == {
        "allele_symbol": "fh111",
        "allele_id": "ZFIN:ZDB-ALT-160602-14",
        "is_transgenic": False,
        "alteration_type": "point_mutation",
        "alteration_label": "Allele with one point mutation",
        "mutagen": "ENU",
        "institution": "Fred Hutchinson Cancer Research Center",
        "constructs": [],
        "affected_genes": [{"gene_symbol": "snapc1b", "gene_id": "ZFIN:ZDB-GENE-040426-716"}],
    }


def test_gene_symbol_finds_its_alleles(zfin_client):
    body = zfin_client.get("/api/zfin/alleles", params={"q": "fgf8a"}).json()
    assert [r["allele_symbol"] for r in body["results"]] == ["ti282a"]


def test_transgenic_hit_carries_the_construct(zfin_client):
    body = zfin_client.get("/api/zfin/alleles", params={"q": "w200Tg"}).json()
    hit = body["results"][0]
    assert hit["is_transgenic"] is True
    assert hit["alteration_type"] == "transgenic_insertion"
    assert hit["constructs"] == [
        {"construct_id": "ZFIN:ZDB-TGCONSTRCT-130130-3", "construct_name": "Tg(mpeg1:YFP)"}
    ]
    assert hit["affected_genes"] == []


def test_coinjected_line_aggregates_to_one_record_with_both_constructs(zfin_client):
    body = zfin_client.get("/api/zfin/alleles", params={"q": "gz13Tg"}).json()
    assert body["total_matches"] == 1
    assert [c["construct_name"] for c in body["results"][0]["constructs"]] == [
        "Tg2(krt4:GFP)",
        "Tg2(mylpfa:RFP)",
    ]
    # And a construct fragment from either row finds the line.
    body = zfin_client.get("/api/zfin/alleles", params={"q": "mylpfa"}).json()
    assert "gz13Tg" in [r["allele_symbol"] for r in body["results"]]


def test_institution_from_registered_prefix(zfin_client):
    """The prefix gives the REGISTERING INSTITUTION — deliberately not called
    "lab": ZFIN's per-feature Lab of Origin is curated separately and can
    differ (la012336Tg: prefix registrant UCLA, lab "Burgess & Lin Lab")."""

    def institution_of(symbol):
        body = zfin_client.get("/api/zfin/alleles", params={"q": symbol}).json()
        return body["results"][0]["institution"]

    # Vendored registry (line_designations.tsv): longest prefix + digit boundary.
    assert institution_of("w200Tg") == "University of Washington"
    assert institution_of("a101") == "Harvard University"
    assert institution_of("gz13Tg") == "The National University of Singapore"
    # 1996 Tübingen two-letter screen codes predate the registry: named fallback.
    assert institution_of("ti282a") == "Tübingen (big-screen designation)"


def test_identical_repeat_rows_collapse(zfin_client):
    body = zfin_client.get("/api/zfin/alleles", params={"q": "tud121Tg"}).json()
    assert body["total_matches"] == 1
    assert len(body["results"][0]["constructs"]) == 1


def test_construct_fragment_finds_the_transgene(zfin_client):
    body = zfin_client.get("/api/zfin/alleles", params={"q": "mpeg1"}).json()
    assert "w200Tg" in [r["allele_symbol"] for r in body["results"]]


def test_unmapped_so_type_keeps_the_label(zfin_client):
    body = zfin_client.get("/api/zfin/alleles", params={"q": "fh900"}).json()
    hit = body["results"][0]
    assert hit["alteration_type"] is None
    assert hit["alteration_label"] == "Allele"


def test_so_root_term_maps_to_sequence_alteration(zfin_client):
    body = zfin_client.get("/api/zfin/alleles", params={"q": "a101"}).json()
    assert body["results"][0]["alteration_type"] == "sequence_alteration"


def test_non_allele_relationships_are_not_affected_genes(zfin_client):
    body = zfin_client.get("/api/zfin/alleles", params={"q": "fh901"}).json()
    assert body["results"][0]["affected_genes"] == []


def test_prefix_search_ranks_and_limits(zfin_client):
    body = zfin_client.get("/api/zfin/alleles", params={"q": "fh", "limit": 2}).json()
    assert body["total_matches"] == 3
    assert [r["allele_symbol"] for r in body["results"]] == ["fh111", "fh900"]


def test_empty_query_is_rejected(zfin_client):
    assert zfin_client.get("/api/zfin/alleles", params={"q": ""}).status_code == 422


def test_wildtypes_sorted_with_curies(zfin_client):
    body = zfin_client.get("/api/zfin/wildtypes").json()
    assert [w["name"] for w in body] == ["AB", "TU", "WIK"]
    assert body[0]["fish_id"] == "ZFIN:ZDB-FISH-150901-27842"
    assert body[0]["genotype_id"] == "ZFIN:ZDB-GENO-960809-7"


def test_missing_downloads_give_503_with_fetch_hint(tmp_path):
    client = _make_client(tmp_path, tmp_path / "nowhere")
    resp = client.get("/api/zfin/alleles", params={"q": "fh111"})
    assert resp.status_code == 503
    assert "fetch-zfin" in resp.json()["detail"]
    assert client.get("/api/zfin/wildtypes").status_code == 503
