from __future__ import annotations

"""End-to-end test: GET /studies/{id} returns the full nested graph."""

from fastapi.testclient import TestClient


def test_get_study_returns_nested_experiments_exposures_observations(
    client: TestClient,
) -> None:
    study = client.post(
        "/studies",
        json={
            "publication": "PMID:333",
            "lab": "ZFIN:ZDB-LAB-1-1",
            "annotator": ["ORCID:0000-0000-0000-0000"],
            "experiment": [],
        },
    ).json()

    exp = client.post(
        f"/studies/{study['id']}/experiments",
        json={
            "standard_rearing_condition": True,
            "fish": {"zfin_id": "ZFIN:ZDB-GENO-990101-3", "name": "AB"},
            "control": [],
            "exposure_event": [],
        },
    ).json()

    exposure = client.post(
        f"/experiments/{exp['id']}/exposures",
        json={
            "exposure_start_stage": "ZFS:0000011",
            "exposure_end_stage": "ZFS:0000039",
            "stressor": [
                {
                    "chemical_id": {
                        "uri": "http://purl.obolibrary.org/obo/CHEBI_33216",
                        "chebi_id": "CHEBI:33216",
                        "cas_id": "80-05-7",
                        "chemical_name": "bisphenol A",
                    },
                    "concentration": {"unit": "µg/L", "numeric_value": "100"},
                }
            ],
            "phenotype_observation": [],
        },
    ).json()

    client.post(
        f"/exposures/{exposure['id']}/observations",
        json={
            "phenotype": [
                {
                    "stage": "ZFS:0000035",
                    "severity": "moderate",
                    "phenotype_term_id": {
                        "term_uri": "ZP:0105827",
                        "term_label": "pericardial region edematous, abnormal",
                    },
                }
            ],
            "image": [],
            "control_image": [],
        },
    )

    res = client.get(f"/studies/{study['id']}")
    assert res.status_code == 200, res.text
    body = res.json()

    assert body["publication"] == "PMID:333"
    assert len(body["experiment"]) == 1
    [got_exp] = body["experiment"]
    assert got_exp["fish"]["name"] == "AB"
    assert len(got_exp["exposure_event"]) == 1
    [got_ee] = got_exp["exposure_event"]
    assert got_ee["exposure_start_stage"] == "ZFS:0000011"
    assert got_ee["stressor"][0]["chemical_id"]["chebi_id"] == "CHEBI:33216"
    assert len(got_ee["phenotype_observation"]) == 1
    [got_obs] = got_ee["phenotype_observation"]
    assert got_obs["phenotype"][0]["severity"] == "moderate"
