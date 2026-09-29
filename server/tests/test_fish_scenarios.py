"""The FISH.pdf 'gross scenarios' round-trip through the API.

Fish has no name slot — display strings are derived, and the tank's nickname
lives on FishTankEntry. Each payload below is the exact FishCreate JSON the
fish widget will emit, one
per scenario in the curation slides: wild-type, single mutant (homo and het on
AB), double mutant, single and multiple transgenics, and the everything case
(mutant + transgenic + background + parental zygosity), plus a morphant
(wild-type + injected morpholino). The curator enters the
alleles and the background; fish_zfin_id and genotype_zfin_id are the ZFIN
records that composition maps to (real ids here — a fish's ZDB-FISH id is
distinct from its genotype's ZDB-GENO id, and alleles are ZDB-ALT features).

Posting a study + experiment per scenario proves the generated create models
accept the shapes and the ORM graph stores and returns them intact.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

SCENARIOS: dict[str, dict] = {
    "wild-type AB": {
        "fish_zfin_id": "ZFIN:ZDB-FISH-150901-27842",
        "genotype_zfin_id": "ZFIN:ZDB-GENO-960809-7",
        # AB is its own background: a wild-type line carries no alterations.
        "background_name": "AB",
        "background_zfin_id": "ZFIN:ZDB-GENO-960809-7",
    },
    "single mutant, homozygous": {
        "fish_zfin_id": "ZFIN:ZDB-FISH-150901-20282",
        "genotype_zfin_id": "ZFIN:ZDB-GENO-071127-8",
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
    "single mutant, het on AB": {
        "fish_zfin_id": "ZFIN:ZDB-FISH-150901-20750",
        "genotype_zfin_id": "ZFIN:ZDB-GENO-070209-1",
        "mutant_allele": [
            {
                "allele_id": "ZFIN:ZDB-ALT-980203-1091",
                "allele_symbol": "ti282a",
                "affected_gene_id": "ZFIN:ZDB-GENE-990415-72",
                "affected_gene_symbol": "fgf8a",
                "zygosity": "heterozygous",
            }
        ],
        "background_name": "AB",
        "background_zfin_id": "ZFIN:ZDB-GENO-960809-7",
    },
    "double mutant": {
        "fish_zfin_id": "ZFIN:ZDB-FISH-150901-29355",
        "genotype_zfin_id": "ZFIN:ZDB-GENO-071012-3",
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
    "single transgenic": {
        "fish_zfin_id": "ZFIN:ZDB-FISH-150901-3654",
        "genotype_zfin_id": "ZFIN:ZDB-GENO-011017-4",
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
    "multiple transgenics": {
        "fish_zfin_id": "ZFIN:ZDB-FISH-150901-23010",
        "genotype_zfin_id": "ZFIN:ZDB-GENO-070329-2",
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
    "morphant: wild-type + injected reagent": {
        # ZFIN registers reagent-carrying fish too: AB + MO1-gata1a is a real
        # record whose id differs from plain AB's, though the genotype id is
        # AB's own (the injection is transient, not part of the genotype).
        "fish_zfin_id": "ZFIN:ZDB-FISH-150901-25118",
        "genotype_zfin_id": "ZFIN:ZDB-GENO-960809-7",
        "transient_reagent": [
            {
                "reagent_id": "ZFIN:ZDB-MRPHLNO-050208-10",
                "reagent_symbol": "MO1-gata1a",
                "reagent_type": "morpholino",
                "affected_gene_id": "ZFIN:ZDB-GENE-980526-476",
                "affected_gene_symbol": "gata1a",
            }
        ],
        "background_name": "AB",
        "background_zfin_id": "ZFIN:ZDB-GENO-960809-7",
    },
    "everything, with parental zygosity": {
        "fish_zfin_id": "ZFIN:ZDB-FISH-160714-24",
        "genotype_zfin_id": "ZFIN:ZDB-GENO-160714-23",
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
        "background_name": "AB",
        "background_zfin_id": "ZFIN:ZDB-GENO-960809-7",
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

        assert got["fish_zfin_id"] == fish["fish_zfin_id"], label
        assert got["genotype_zfin_id"] == fish["genotype_zfin_id"], label

        want_mut = {(m["allele_symbol"], m.get("zygosity")) for m in fish.get("mutant_allele", [])}
        got_mut = {(m["allele_symbol"], m.get("zygosity")) for m in got["mutant_allele"]}
        assert got_mut == want_mut, label

        want_tg = {t["allele_symbol"] for t in fish.get("transgenic_allele", [])}
        got_tg = {t["allele_symbol"] for t in got["transgenic_allele"]}
        assert got_tg == want_tg, label

        want_str = {r["reagent_symbol"] for r in fish.get("transient_reagent", [])}
        got_str = {r["reagent_symbol"] for r in got["transient_reagent"]}
        assert got_str == want_str, label

        assert got["background_name"] == fish.get("background_name"), label
        assert got["background_zfin_id"] == fish.get("background_zfin_id"), label


def test_parental_zygosity_round_trips(client: TestClient) -> None:
    got = _post_experiment(client, SCENARIOS["everything, with parental zygosity"])["fish"]
    [mutant] = got["mutant_allele"]
    assert mutant["zygosity"] == "homozygous"
    assert mutant["mother_zygosity"] == "heterozygous"
    assert mutant["father_zygosity"] == "heterozygous"


def test_transient_reagent_round_trips(client: TestClient) -> None:
    got = _post_experiment(client, SCENARIOS["morphant: wild-type + injected reagent"])["fish"]
    [reagent] = got["transient_reagent"]
    assert reagent["reagent_type"] == "morpholino"
    assert reagent["reagent_id"] == "ZFIN:ZDB-MRPHLNO-050208-10"
    assert reagent["affected_gene_symbol"] == "gata1a"
