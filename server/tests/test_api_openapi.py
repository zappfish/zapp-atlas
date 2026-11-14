"""The client's copy of the OpenAPI document must match what the server serves."""

from pathlib import Path

from zapp_atlas.api.openapi import openapi_document

CLIENT_COPY = Path(__file__).resolve().parents[2] / "client" / "src" / "api" / "openapi.json"


def test_the_clients_openapi_document_is_current() -> None:
    """The client's request and response types are generated from this file.

    If it is stale, the client is typed against an API the server no longer
    serves. Regenerate it, and the types, with ``just api-types``.
    """
    assert CLIENT_COPY.read_text() == openapi_document(), (
        "client/src/api/openapi.json is out of date; run `just api-types`"
    )
