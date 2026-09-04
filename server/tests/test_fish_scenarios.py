"""The FISH.pdf 'gross scenarios' round-trip through the API.

Each payload below is the exact FishCreate JSON the fish widget will emit, one
per scenario in the curation slides: wild-type, single mutant (homo and het on
AB), double mutant, single and multiple transgenics, and the everything case
(mutant + transgenic + background + parental zygosity). ZFIN ids are the real
ones — a fish's ZDB-FISH id is distinct from its genotype's ZDB-GENO id, and
alleles are ZDB-ALT genomic features.

Posting a study + experiment per scenario proves the generated create models
accept the shapes and the ORM graph stores and returns them intact.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

SCENARIOS: dict[str, dict] = {
    "wild-type AB": {
        "name": "AB",
        "fish_zfin_id": "ZFIN:ZDB-FISH-150901-27842",
        "genotype": {
            "genotype_zfin_id": "ZFIN:ZDB-GENO-960809-7",
            "genotype_name": "AB",
            # AB is its own background: a wild-type line carries no alterations.
            "background": {
                "genotype_name": "AB",
                "genotype_zfin_id": "ZFIN:ZDB-GENO-960809-7",
            },
        },
    },
    "single mutant, homozygous": {
        "name": "fgf8a<ti282a/ti282a>",
        "fish_zfin_id": "ZFIN:ZDB-FISH-150901-20282",
        "genotype": {
            "genotype_zfin_id": "ZFIN:ZDB-GENO-071127-8",
            "genotype_name": "fgf8a<ti282a/ti282a>",
            "mutant_allele": [
                {
                    "allele_id": "ZFIN:ZDB-ALT-980203-1091",
                    "allele_symbol": "ti282a",
                    "alteration_type": "point_mutation",
                    "affected_gene_id": "ZFIN:ZDB-GENE-990415-72",
                    "affected_gene_symbol": "fgf8a",
                    "zygosity": "homozygous",
                }
            ],
        },
    },
    "single mutant, het on AB": {
        "name": "fgf8a<ti282a/+> (AB)",
        "fish_zfin_id": "ZFIN:ZDB-FISH-150901-20750",
        "genotype": {
            "genotype_zfin_id": "ZFIN:ZDB-GENO-070209-1",
            "genotype_name": "fgf8a<ti282a/+> (AB)",
            "mutant_allele": [
                {
                    "allele_id": "ZFIN:ZDB-ALT-980203-1091",
                    "allele_symbol": "ti282a",
                    "affected_gene_id": "ZFIN:ZDB-GENE-990415-72",
                    "affected_gene_symbol": "fgf8a",
                    "zygosity": "heterozygous",
                }
            ],
            "background": {
                "genotype_name": "AB",
                "genotype_zfin_id": "ZFIN:ZDB-GENO-960809-7",
            },
        },
    },
    "double mutant": {
        "name": "fgf8a<ti282a/ti282a>; rerea<tb210/tb210>",
        "fish_zfin_id": "ZFIN:ZDB-FISH-150901-29355",
        "genotype": {
            "genotype_zfin_id": "ZFIN:ZDB-GENO-071012-3",
            "genotype_name": "fgf8a<ti282a/ti282a>; rerea<tb210/tb210>",
            "mutant_allele": [
                {
                    "allele_id": "ZFIN:ZDB-ALT-980203-1091",
                    "allele_symbol": "ti282a",
                    "affected_gene_symbol": "fgf8a",
                    "zygosity": "homozygous",
                },
                {
                    "allele_id": "ZFIN:ZDB-ALT-980203-1102",
                    "allele_symbol": "tb210",
                    "affected_gene_symbol": "rerea",
                    "zygosity": "homozygous",
                },
            ],
        },
    },
    "single transgenic": {
        "name": "y1Tg",
        "fish_zfin_id": "ZFIN:ZDB-FISH-150901-3654",
        "genotype": {
            "genotype_zfin_id": "ZFIN:ZDB-GENO-011017-4",
            "genotype_name": "y1Tg",
            "transgenic_allele": [
                {
                    "allele_id": "ZFIN:ZDB-ALT-011017-8",
                    "allele_symbol": "y1Tg",
                    "construct_name": "Tg(fli1:EGFP)",
                    "alteration_type": "transgenic_insertion",
                    "affected_gene_id": "ZFIN:ZDB-GENE-980526-426",
                    "affected_gene_symbol": "fli1",
                    "zygosity": "unknown",
                }
            ],
        },
    },
    "multiple transgenics": {
        "name": "sd2Tg; y1Tg",
        "fish_zfin_id": "ZFIN:ZDB-FISH-150901-23010",
        "genotype": {
            "genotype_zfin_id": "ZFIN:ZDB-GENO-070329-2",
            "genotype_name": "sd2Tg; y1Tg",
            "transgenic_allele": [
                {
                    "allele_id": "ZFIN:ZDB-ALT-051223-6",
                    "allele_symbol": "sd2Tg",
                    "construct_name": "Tg(gata1a:DsRed)",
                    "zygosity": "unknown",
                },
                {
                    "allele_id": "ZFIN:ZDB-ALT-011017-8",
                    "allele_symbol": "y1Tg",
                    "construct_name": "Tg(fli1:EGFP)",
                    "zygosity": "unknown",
                },
            ],
        },
    },
    "everything, with parental zygosity": {
        "name": "snapc1b<fh111/fh111>; w200Tg (AB)",
        "fish_zfin_id": "ZFIN:ZDB-FISH-160714-24",
        "genotype": {
            "genotype_zfin_id": "ZFIN:ZDB-GENO-160714-23",
            "genotype_name": "snapc1b<fh111/fh111>; w200Tg (AB)",
            "mutant_allele": [
                {
                    "allele_id": "ZFIN:ZDB-ALT-160602-14",
                    "allele_symbol": "fh111",
                    "alteration_type": "point_mutation",
                    "affected_gene_symbol": "snapc1b",
                    "zygosity": "homozygous",
                    "mother_zygosity": "heterozygous",
                    "father_zygosity": "heterozygous",
                }
            ],
            "transgenic_allele": [
                {
                    "allele_id": "ZFIN:ZDB-ALT-130130-3",
                    "allele_symbol": "w200Tg",
                    "construct_id": "ZFIN:ZDB-TGCONSTRCT-130130-3",
                    "construct_name": "Tg(mpeg1:YFP)",
                    "alteration_type": "transgenic_insertion",
                    "zygosity": "unknown",
                }
            ],
            "background": {
                "genotype_name": "AB",
                "genotype_zfin_id": "ZFIN:ZDB-GENO-960809-7",
            },
        },
    },
}


def _post_experiment(client: TestClient, fish: dict) -> dict:
    study = client.post(
        "/api/studies",
        json={
            "publication": "PMID:123456",
            "lab": "ZFIN:ZDB-LAB-1-1",
            "annotator": ["ORCID:0000-0000-0000-0000"],
            "experiment": [],
        },
    ).json()
    res = client.post(
        f"/api/studies/{study['id']}/experiments",
        json={
            "standard_rearing_condition": True,
            "fish": fish,
            "control": [],
            "exposure_event": [],
        },
    )
    assert res.status_code == 201, res.text
    return client.get(f"/api/experiments/{res.json()['id']}").json()


def test_every_scenario_round_trips(client: TestClient) -> None:
    for label, fish in SCENARIOS.items():
        got = _post_experiment(client, fish)["fish"]
        want_geno = fish.get("genotype", {})

        assert got["name"] == fish["name"], label
        assert got["fish_zfin_id"] == fish["fish_zfin_id"], label
        geno = got["genotype"]
        assert geno["genotype_zfin_id"] == want_geno.get("genotype_zfin_id"), label

        want_mut = {
            (m["allele_symbol"], m.get("zygosity")) for m in want_geno.get("mutant_allele", [])
        }
        got_mut = {(m["allele_symbol"], m.get("zygosity")) for m in geno["mutant_allele"]}
        assert got_mut == want_mut, label

        want_tg = {t["allele_symbol"] for t in want_geno.get("transgenic_allele", [])}
        got_tg = {t["allele_symbol"] for t in geno["transgenic_allele"]}
        assert got_tg == want_tg, label

        want_bg = want_geno.get("background")
        if want_bg is None:
            assert geno["background"] is None, label
        else:
            assert geno["background"]["genotype_name"] == want_bg["genotype_name"], label


def test_parental_zygosity_round_trips(client: TestClient) -> None:
    got = _post_experiment(client, SCENARIOS["everything, with parental zygosity"])["fish"]
    [mutant] = got["genotype"]["mutant_allele"]
    assert mutant["zygosity"] == "homozygous"
    assert mutant["mother_zygosity"] == "heterozygous"
    assert mutant["father_zygosity"] == "heterozygous"
