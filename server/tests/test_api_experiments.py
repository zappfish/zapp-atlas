"""API tests for Experiment endpoints."""

from fastapi.testclient import TestClient
from support import study_fields


def _create_study(client: TestClient, group: int) -> int:
    payload = {
        "publication": "PMID:123456",
        "lab": "ZFIN:ZDB-LAB-1-1",
        **study_fields(group),
    }
    res = client.post("/api/studies", json=payload)
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_experiment_create_for_study_then_get(client: TestClient, group: int) -> None:
    study_id = _create_study(client, group)

    exp_payload = {
        "standard_rearing_condition": True,
        "rearing_condition_comment": "",
        "fish": {"background_zfin_id": "ZFIN:ZDB-GENO-960809-7", "background_name": "AB"},
        "control": [],
    }

    create_res = client.post(f"/api/studies/{study_id}/experiments", json=exp_payload)
    assert create_res.status_code == 201, create_res.text
    created = create_res.json()
    assert "id" in created

    get_res = client.get(f"/api/experiments/{created['id']}")
    assert get_res.status_code == 200, get_res.text
    got = get_res.json()
    assert got["id"] == created["id"]


def test_experiment_create_missing_study_404(client: TestClient, group: int) -> None:
    exp_payload = {
        "standard_rearing_condition": True,
        "fish": {"background_zfin_id": "ZFIN:ZDB-GENO-960809-7", "background_name": "AB"},
        "control": [],
    }
    res = client.post("/api/studies/999999/experiments", json=exp_payload)
    assert res.status_code == 404


def test_experiment_get_missing_404(client: TestClient, group: int) -> None:
    res = client.get("/api/experiments/999999")
    assert res.status_code == 404


def test_experiment_put_updates_rearing_and_fish(client: TestClient, group: int) -> None:
    study_id = _create_study(client, group)
    exp = client.post(
        f"/api/studies/{study_id}/experiments",
        json={
            "standard_rearing_condition": True,
            "rearing_condition_comment": "",
            "fish": {"background_zfin_id": "ZFIN:ZDB-GENO-960809-7", "background_name": "AB"},
            "control": [],
        },
    ).json()

    res = client.put(
        f"/api/experiments/{exp['id']}",
        json={
            "standard_rearing_condition": False,
            "rearing_condition_comment": "temperature 24C",
            "fish": {
                "background_zfin_id": "ZFIN:ZDB-GENO-990623-3",
                "background_name": "TU",
                "allele": [
                    {
                        "allele_zfin_id": "ZFIN:ZDB-ALT-980203-1091",
                        "allele_symbol": "ti282a",
                        "alteration_type": "point_mutation",
                        "affected_gene_zfin_id": "ZFIN:ZDB-GENE-990415-72",
                        "affected_gene_symbol": "fgf8a",
                        "zygosity": "homozygous",
                    }
                ],
            },
        },
    )
    assert res.status_code == 200, res.text
    patched = res.json()
    assert patched["standard_rearing_condition"] is False
    assert patched["rearing_condition_comment"] == "temperature 24C"
    assert patched["fish"]["background_name"] == "TU"
    # ti282a homozygous on TU is a genotype the tests' ZFIN records have.
    assert patched["fish"]["genotype_zfin_id"] == "ZFIN:ZDB-GENO-180101-1"
    [allele] = patched["fish"]["allele"]
    assert (allele["allele_symbol"], allele["zygosity"]) == ("ti282a", "homozygous")
    assert allele["mother_zygosity"] is None


def test_experiment_put_missing_404(client: TestClient, group: int) -> None:
    res = client.put("/api/experiments/999999", json={"rearing_condition_comment": "x"})
    assert res.status_code == 404
