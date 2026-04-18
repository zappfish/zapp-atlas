from __future__ import annotations

"""ZFIN autocomplete proxy tests."""

import httpx
import respx
from fastapi.testclient import TestClient


ZFIN_URL = "https://zfin.org/action/quicksearch/autocomplete"


@respx.mock
def test_zfin_autocomplete_proxies_and_returns_results(client: TestClient) -> None:
    upstream = respx.get(ZFIN_URL).mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": "ZDB-FISH-150901-27842",
                    "name": "AB",
                    "value": "AB",
                    "url": "/ZDB-FISH-150901-27842",
                    "category": "Fish",
                },
            ],
        )
    )

    res = client.get("/zfin/fish-autocomplete", params={"q": "AB"})
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body, list)
    assert body[0]["id"] == "ZDB-FISH-150901-27842"
    assert body[0]["name"] == "AB"

    assert upstream.called
    call = upstream.calls[0]
    assert call.request.url.params.get("q") == "AB"
    assert call.request.url.params.get("category") == "Fish"


@respx.mock
def test_zfin_autocomplete_requires_q(client: TestClient) -> None:
    res = client.get("/zfin/fish-autocomplete")
    assert res.status_code == 422


@respx.mock
def test_zfin_autocomplete_upstream_error_is_502(client: TestClient) -> None:
    respx.get(ZFIN_URL).mock(return_value=httpx.Response(500))
    res = client.get("/zfin/fish-autocomplete", params={"q": "AB"})
    assert res.status_code == 502
