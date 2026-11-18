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


@pytest.fixture
def extdata_dir(zfin_db):
    return zfin_db.parent


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
