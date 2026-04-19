from __future__ import annotations

"""OLS autocomplete proxy tests."""

import httpx
import respx
from fastapi.testclient import TestClient

from server.ontology import OLS_BASE_URL


@respx.mock
def test_exposure_route_autocomplete_proxies_to_ols_exo(client: TestClient) -> None:
    upstream = respx.get(f"{OLS_BASE_URL}/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "response": {
                    "docs": [
                        {
                            "iri": "http://purl.obolibrary.org/obo/ExO_0000057",
                            "obo_id": "ExO:0000057",
                            "label": "inhalation route",
                            "ontology_name": "exo",
                        }
                    ]
                }
            },
        )
    )

    res = client.get("/api/ols/exposure-route-autocomplete", params={"q": "inhalation"})
    assert res.status_code == 200
    body = res.json()
    assert body == [{"term_uri": "ExO:0000057", "term_label": "inhalation route"}]

    # The call went to OLS with the right ontology + query.
    assert upstream.called
    call = upstream.calls[0]
    assert call.request.url.params["ontology"] == "exo"
    assert call.request.url.params["q"] == "inhalation"


@respx.mock
def test_exposure_type_autocomplete_proxies_to_ols_ecto(client: TestClient) -> None:
    upstream = respx.get(f"{OLS_BASE_URL}/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "response": {
                    "docs": [
                        {
                            "iri": "http://purl.obolibrary.org/obo/ECTO_0000001",
                            "obo_id": "ECTO:0000001",
                            "label": "exposure to stressor",
                        }
                    ]
                }
            },
        )
    )

    res = client.get("/api/ols/exposure-type-autocomplete", params={"q": "stressor"})
    assert res.status_code == 200
    assert res.json() == [{"term_uri": "ECTO:0000001", "term_label": "exposure to stressor"}]
    assert upstream.calls[0].request.url.params["ontology"] == "ecto"


@respx.mock
def test_autocomplete_requires_q(client: TestClient) -> None:
    assert client.get("/api/ols/exposure-route-autocomplete").status_code == 422


@respx.mock
def test_autocomplete_upstream_error_is_502(client: TestClient) -> None:
    respx.get(f"{OLS_BASE_URL}/search").mock(return_value=httpx.Response(500))
    res = client.get("/api/ols/exposure-route-autocomplete", params={"q": "x"})
    assert res.status_code == 502
