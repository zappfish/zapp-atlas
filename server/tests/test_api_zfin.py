"""/api/zfin against a bundle holding the database built from tests/zfin_fixture."""

import pytest
from fastapi.testclient import TestClient

from zapp_atlas.main import create_app
from zapp_atlas.settings import AppSettings

FH111 = "ZFIN:ZDB-ALT-160602-14"


def make_client(extdata_dir) -> TestClient:
    settings = AppSettings(skip_seed=True, extdata_dir=extdata_dir, _env_file=None)
    return TestClient(create_app(settings))


@pytest.fixture(scope="module")
def client(zfin_db) -> TestClient:
    return make_client(zfin_db.parent)


def test_without_a_bundle_lookups_answer_503(tmp_path):
    res = make_client(tmp_path).get("/api/zfin/wildtypes")
    assert res.status_code == 503
    assert "just extdata" in res.json()["detail"]


def test_status_names_the_snapshot(client):
    res = client.get("/api/zfin/status")
    assert res.status_code == 200
    assert res.json() == {
        "zfin_date": "2026.11.01",
        "counts": {"wildtype": 2, "allele": 7, "genotype": 8, "fish": 9, "reagent": 1},
    }


def test_wildtypes(client):
    res = client.get("/api/zfin/wildtypes")
    assert res.status_code == 200
    assert res.json()[0] == {
        "fish_id": "ZFIN:ZDB-FISH-150901-27842",
        "genotype_id": "ZFIN:ZDB-GENO-960809-7",
        "name": "AB",
        "abbreviation": "AB",
    }


def test_allele_search(client):
    res = client.get("/api/zfin/alleles", params={"q": "fgf8a"})
    assert res.status_code == 200
    body = res.json()
    assert body["query"] == "fgf8a"
    assert body["total_matches"] == 1
    (allele,) = body["results"]
    assert allele["symbol"] == "ti282a"
    assert allele["so_id"] == "SO:1000008"
    assert allele["genes"] == [{"gene_id": "ZFIN:ZDB-GENE-990415-72", "symbol": "fgf8a"}]
    assert allele["constructs"] == []


def test_allele_search_is_limited_and_reports_the_total(client):
    res = client.get("/api/zfin/alleles", params={"q": "tg", "limit": 1})
    assert res.json()["total_matches"] == 2
    assert len(res.json()["results"]) == 1


def test_allele_search_validates_its_query(client):
    assert client.get("/api/zfin/alleles").status_code == 422
    assert client.get("/api/zfin/alleles", params={"q": ""}).status_code == 422
    assert client.get("/api/zfin/alleles", params={"q": "a", "limit": 0}).status_code == 422


def test_allele_by_id(client):
    res = client.get("/api/zfin/alleles/ZFIN:ZDB-ALT-070117-1")
    assert res.status_code == 200
    body = res.json()
    assert body["is_transgenic"] is True
    assert [c["name"] for c in body["constructs"]] == ["Tg(fli1a:EGFP)", "Tg(gata1:DsRed)"]


def test_genotype_by_id(client):
    res = client.get("/api/zfin/genotypes/ZFIN:ZDB-GENO-160602-1")
    assert res.status_code == 200
    body = res.json()
    assert body["name"] == "snapc1b<sup>fh111/+</sup>"
    assert body["unique_name"] == "fh111[1,1,2]AB"
    assert body["alleles"] == [
        {
            "allele_id": FH111,
            "symbol": "fh111",
            "zygosity": "heterozygous",
            "mother_zygosity": "heterozygous",
            "father_zygosity": "homozygous",
        }
    ]
    assert [b["name"] for b in body["backgrounds"]] == ["AB", "TU"]


def test_fish_by_id(client):
    res = client.get("/api/zfin/fish/ZFIN:ZDB-FISH-160602-2")
    assert res.status_code == 200
    body = res.json()
    assert body["genotype"] == {
        "genotype_id": "ZFIN:ZDB-GENO-160602-1",
        "name": "snapc1b<sup>fh111/+</sup>",
        "name_plain": "snapc1bfh111/+",
    }
    (reagent,) = body["reagents"]
    assert reagent["kind"] == "morpholino"
    assert [g["symbol"] for g in reagent["genes"]] == ["fgf8a", "fgf8b"]


def test_unknown_ids_are_404(client):
    for path in (
        "alleles/ZFIN:ZDB-ALT-1-1",
        "genotypes/ZFIN:ZDB-GENO-1-1",
        "fish/ZFIN:ZDB-FISH-1-1",
    ):
        assert client.get(f"/api/zfin/{path}").status_code == 404
