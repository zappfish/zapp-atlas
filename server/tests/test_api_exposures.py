from __future__ import annotations

"""API tests for Exposure event endpoints."""

import httpx
import respx
from fastapi.testclient import TestClient

from server.ontology import OLS_BASE_URL


def _mock_exo_water_route() -> None:
    """Stub OLS so ``ExO:0000057`` validates and resolves to a label."""
    respx.get(f"{OLS_BASE_URL}/ontologies/exo/terms").mock(
        return_value=httpx.Response(
            200,
            json={
                "_embedded": {
                    "terms": [
                        {
                            "iri": "http://purl.obolibrary.org/obo/ExO_0000057",
                            "obo_id": "ExO:0000057",
                            "label": "inhalation route",
                        }
                    ]
                }
            },
        )
    )
    # Ancestors include the "exposure route" root so reachability passes.
    respx.get(
        f"{OLS_BASE_URL}/ontologies/exo/terms/"
        "http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FExO_0000057/ancestors"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "_embedded": {
                    "terms": [
                        {
                            "iri": "http://purl.obolibrary.org/obo/ExO_0000055",
                            "obo_id": "ExO:0000055",
                            "label": "exposure route",
                        }
                    ]
                }
            },
        )
    )


def _create_study_and_experiment(client: TestClient) -> tuple[int, int]:
    study = client.post(
        "/api/studies",
        json={
            "publication": "PMID:111",
            "lab": "ZFIN:ZDB-LAB-1-1",
            "annotator": ["ORCID:0000-0000-0000-0000"],
            "experiment": [],
        },
    ).json()
    exp = client.post(
        f"/api/studies/{study['id']}/experiments",
        json={
            "standard_rearing_condition": True,
            "fish": {"zfin_id": "ZFIN:ZDB-GENO-990101-1", "name": "AB"},
            "control": [],
            "exposure_event": [],
        },
    ).json()
    return study["id"], exp["id"]


def test_create_exposure_for_experiment(client: TestClient) -> None:
    _, exp_id = _create_study_and_experiment(client)

    payload = {
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
    }

    res = client.post(f"/api/experiments/{exp_id}/exposures", json=payload)
    assert res.status_code == 201, res.text
    created = res.json()
    assert "id" in created
    assert created["exposure_start_stage"] == "ZFS:0000011"
    assert created["stressor"][0]["chemical_id"]["chebi_id"] == "CHEBI:33216"


def test_create_exposure_missing_experiment_404(client: TestClient) -> None:
    res = client.post(
        "/api/experiments/999999/exposures",
        json={"stressor": [], "phenotype_observation": []},
    )
    assert res.status_code == 404


def test_get_exposure(client: TestClient) -> None:
    _, exp_id = _create_study_and_experiment(client)
    created = client.post(
        f"/api/experiments/{exp_id}/exposures",
        json={"stressor": [], "phenotype_observation": []},
    ).json()

    res = client.get(f"/api/exposures/{created['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == created["id"]


def test_get_exposure_missing_404(client: TestClient) -> None:
    assert client.get("/api/exposures/999999").status_code == 404


def test_patch_exposure_updates_fields(client: TestClient) -> None:
    _, exp_id = _create_study_and_experiment(client)
    created = client.post(
        f"/api/experiments/{exp_id}/exposures",
        json={
            "comment": "",
            "exposure_start_stage": "ZFS:0000011",
            "stressor": [],
            "phenotype_observation": [],
        },
    ).json()

    res = client.patch(
        f"/api/exposures/{created['id']}",
        json={"comment": "revised note", "exposure_start_stage": "ZFS:0000012"},
    )
    assert res.status_code == 200, res.text
    patched = res.json()
    assert patched["comment"] == "revised note"
    assert patched["exposure_start_stage"] == "ZFS:0000012"


def test_patch_exposure_missing_404(client: TestClient) -> None:
    assert client.patch("/api/exposures/999999", json={"comment": "x"}).status_code == 404


# -- ontology-validated fields -------------------------------------------------


@respx.mock
def test_create_exposure_with_valid_route_round_trips(client: TestClient) -> None:
    _mock_exo_water_route()
    _, exp_id = _create_study_and_experiment(client)

    res = client.post(
        f"/api/experiments/{exp_id}/exposures",
        json={
            "route": "ExO:0000057",
            "stressor": [],
            "phenotype_observation": [],
        },
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["route"] == "ExO:0000057"

    # The stored term carries the canonical label fetched from OLS.
    got = client.get(f"/api/exposures/{body['id']}").json()
    assert got["route"] == "ExO:0000057"


@respx.mock
def test_create_exposure_with_unknown_route_is_422(client: TestClient) -> None:
    respx.get(f"{OLS_BASE_URL}/ontologies/exo/terms").mock(
        return_value=httpx.Response(200, json={"_embedded": {"terms": []}})
    )
    _, exp_id = _create_study_and_experiment(client)

    res = client.post(
        f"/api/experiments/{exp_id}/exposures",
        json={"route": "ExO:9999999", "stressor": [], "phenotype_observation": []},
    )
    assert res.status_code == 422
    assert "ExO:9999999" in res.text


@respx.mock
def test_create_exposure_with_unreachable_route_is_422(client: TestClient) -> None:
    # Term exists but has no ancestors under ExO:0000055.
    respx.get(f"{OLS_BASE_URL}/ontologies/exo/terms").mock(
        return_value=httpx.Response(
            200,
            json={
                "_embedded": {
                    "terms": [
                        {
                            "iri": "http://purl.obolibrary.org/obo/ExO_0000001",
                            "obo_id": "ExO:0000001",
                            "label": "exposure ontology (root)",
                        }
                    ]
                }
            },
        )
    )
    respx.get(
        f"{OLS_BASE_URL}/ontologies/exo/terms/"
        "http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FExO_0000001/ancestors"
    ).mock(
        return_value=httpx.Response(200, json={"_embedded": {"terms": []}})
    )
    _, exp_id = _create_study_and_experiment(client)

    res = client.post(
        f"/api/experiments/{exp_id}/exposures",
        json={"route": "ExO:0000001", "stressor": [], "phenotype_observation": []},
    )
    assert res.status_code == 422
    assert "reachable" in res.text.lower()


@respx.mock
def test_create_exposure_fails_open_when_ols_down(client: TestClient) -> None:
    respx.get(f"{OLS_BASE_URL}/ontologies/exo/terms").mock(
        return_value=httpx.Response(503)
    )
    _, exp_id = _create_study_and_experiment(client)

    res = client.post(
        f"/api/experiments/{exp_id}/exposures",
        json={"route": "ExO:0000057", "stressor": [], "phenotype_observation": []},
    )
    assert res.status_code == 201, res.text
    assert res.json()["route"] == "ExO:0000057"


@respx.mock
def test_patch_exposure_replaces_route(client: TestClient) -> None:
    _mock_exo_water_route()
    _, exp_id = _create_study_and_experiment(client)

    created = client.post(
        f"/api/experiments/{exp_id}/exposures",
        json={"route": "ExO:0000057", "stressor": [], "phenotype_observation": []},
    ).json()

    # PATCH back to no-route by setting to a different valid term; stub a
    # second term.
    respx.get(f"{OLS_BASE_URL}/ontologies/exo/terms").mock(
        return_value=httpx.Response(
            200,
            json={
                "_embedded": {
                    "terms": [
                        {
                            "iri": "http://purl.obolibrary.org/obo/ExO_0000056",
                            "obo_id": "ExO:0000056",
                            "label": "dermal route",
                        }
                    ]
                }
            },
        )
    )
    respx.get(
        f"{OLS_BASE_URL}/ontologies/exo/terms/"
        "http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FExO_0000056/ancestors"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "_embedded": {
                    "terms": [
                        {"obo_id": "ExO:0000055", "label": "exposure route"}
                    ]
                }
            },
        )
    )

    res = client.patch(
        f"/api/exposures/{created['id']}",
        json={"route": "ExO:0000056"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["route"] == "ExO:0000056"
