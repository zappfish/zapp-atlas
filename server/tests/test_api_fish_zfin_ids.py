"""A saved fish gets its ZFIN ids from the registry, not from the request.

Runs against the database built from tests/zfin_fixture, where fh111 is
registered heterozygous on AB as ZDB-GENO-160602-1 / ZDB-FISH-160602-1.
"""

import pytest
from fastapi.testclient import TestClient
from support import study_fields

AB = {"background_zfin_id": "ZFIN:ZDB-GENO-960809-7", "background_name": "AB"}
FH111 = {
    "allele_zfin_id": "ZFIN:ZDB-ALT-160602-14",
    "allele_symbol": "fh111",
    "zygosity": "heterozygous",
}


def _tank_fish(client: TestClient, group: int, fish: dict) -> dict:
    res = client.post(f"/api/research-groups/{group}/fish-tank", json={"fish": fish})
    assert res.status_code == 201, res.text
    return res.json()["fish"]


def test_a_registered_description_gets_its_ids(client: TestClient, group: int) -> None:
    fish = _tank_fish(client, group, {**AB, "allele": [FH111]})
    assert fish["genotype_zfin_id"] == "ZFIN:ZDB-GENO-160602-1"
    assert fish["fish_zfin_id"] == "ZFIN:ZDB-FISH-160602-1"


def test_a_wild_type_line_is_its_own_genotype(client: TestClient, group: int) -> None:
    fish = _tank_fish(client, group, AB)
    assert fish["genotype_zfin_id"] == AB["background_zfin_id"]
    assert fish["fish_zfin_id"] == "ZFIN:ZDB-FISH-150901-27842"


def test_an_unregistered_description_gets_none(client: TestClient, group: int) -> None:
    fish = _tank_fish(client, group, {**AB, "allele": [{**FH111, "zygosity": "complex"}]})
    assert (fish["genotype_zfin_id"], fish["fish_zfin_id"]) == (None, None)


def test_an_allele_zfin_does_not_have_leaves_the_fish_unmatched(
    client: TestClient, group: int
) -> None:
    # Matching what is left would name wild-type AB, or the fh111 line.
    novel = {"allele_symbol": "unc101", "zygosity": "homozygous"}
    for alleles in ([novel], [FH111, novel]):
        fish = _tank_fish(client, group, {**AB, "allele": alleles})
        assert (fish["genotype_zfin_id"], fish["fish_zfin_id"]) == (None, None)


def test_the_ids_cannot_be_sent(client: TestClient, group: int) -> None:
    res = client.post(
        f"/api/research-groups/{group}/fish-tank",
        json={"fish": {**AB, "fish_zfin_id": "ZFIN:ZDB-FISH-160602-1"}},
    )
    assert res.status_code == 422


def test_an_experiment_fish_is_matched_and_rematched(client: TestClient, group: int) -> None:
    study = client.post(
        "/api/studies", json={**study_fields(group), "nickname": "fh111 study"}
    ).json()
    experiment = client.post(
        f"/api/studies/{study['id']}/experiments", json={"fish": {**AB, "allele": [FH111]}}
    ).json()
    assert experiment["fish"]["fish_zfin_id"] == "ZFIN:ZDB-FISH-160602-1"

    replaced = client.put(f"/api/experiments/{experiment['id']}", json={"fish": AB}).json()
    assert replaced["fish"]["fish_zfin_id"] == "ZFIN:ZDB-FISH-150901-27842"


# -- the names beside the ids ------------------------------------------------


def test_a_part_named_by_id_takes_zfins_name_for_it(client: TestClient, group: int) -> None:
    described = {
        "background_zfin_id": AB["background_zfin_id"],
        "background_name": "Tuebingen",
        "allele": [
            {
                "allele_zfin_id": "ZFIN:ZDB-ALT-980203-1091",
                "allele_symbol": "something else",
                "alteration_type": "deletion",
                "affected_gene_zfin_id": "ZFIN:ZDB-GENE-990415-72",
                "affected_gene_symbol": "wrong",
                "zygosity": "homozygous",
            },
            {
                "allele_zfin_id": "ZFIN:ZDB-ALT-130130-3",
                "allele_symbol": "w200Tg",
                "construct_zfin_id": "ZFIN:ZDB-TGCONSTRCT-130130-3",
                "zygosity": "unknown",
            },
        ],
    }
    fish = _tank_fish(client, group, described)

    assert fish["background_name"] == "AB"
    mutant, transgenic = fish["allele"]
    assert mutant["allele_symbol"] == "ti282a"
    assert mutant["alteration_type"] == "point_mutation"
    assert mutant["affected_gene_symbol"] == "fgf8a"
    assert transgenic["alteration_type"] == "transgenic_insertion"
    # Sent with no name at all, and given one.
    assert transgenic["construct_name"]


@pytest.mark.parametrize(
    "fish",
    [
        {"background_zfin_id": "ZFIN:ZDB-GENO-000000-0"},
        # A genotype ZFIN has, which is not one of its wild-type lines.
        {"background_zfin_id": "ZFIN:ZDB-GENO-160602-1"},
        {"allele": [{**FH111, "allele_zfin_id": "ZFIN:ZDB-ALT-000000-0"}]},
        {"allele": [{**FH111, "affected_gene_zfin_id": "ZFIN:ZDB-GENE-000000-0"}]},
        {"allele": [{**FH111, "construct_zfin_id": "ZFIN:ZDB-TGCONSTRCT-000000-0"}]},
        {
            "transient_reagent": [
                {"reagent_zfin_id": "ZFIN:ZDB-MRPHLNO-000000-0", "reagent_symbol": "MO1-none"}
            ]
        },
    ],
)
def test_an_id_zfin_does_not_have_is_refused(client: TestClient, group: int, fish: dict) -> None:
    res = client.post(f"/api/research-groups/{group}/fish-tank", json={"fish": fish})
    assert res.status_code == 422, res.text
    assert "ZFIN has" in res.text


def test_a_part_described_without_an_id_keeps_its_name(client: TestClient, group: int) -> None:
    novel = {
        "allele_symbol": "unc101",
        "affected_gene_symbol": "a gene of our own",
        "zygosity": "homozygous",
    }
    [allele] = _tank_fish(client, group, {"allele": [novel]})["allele"]
    assert (allele["allele_symbol"], allele["affected_gene_symbol"]) == (
        "unc101",
        "a gene of our own",
    )


class TestWithNoBundle:
    @pytest.fixture
    def extdata_dir(self, tmp_path_factory):
        return tmp_path_factory.mktemp("no-bundle")

    def test_a_fish_named_by_ids_is_not_stored_unchecked(
        self, client: TestClient, group: int
    ) -> None:
        res = client.post(f"/api/research-groups/{group}/fish-tank", json={"fish": AB})
        assert res.status_code == 503, res.text

    def test_a_fish_described_in_words_needs_no_registry(
        self, client: TestClient, group: int
    ) -> None:
        described = {"line_description": "an outbred line from the pet shop"}
        res = client.post(f"/api/research-groups/{group}/fish-tank", json={"fish": described})
        assert res.status_code == 201, res.text
