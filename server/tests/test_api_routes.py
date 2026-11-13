"""The hand-written routes must agree with the layout, and every write must be gated.

The routers are written by hand, so nothing but these tests stops one from
drifting: taking a body the layout does not describe, missing a verb, or
letting an anonymous caller write.
"""

from collections.abc import Iterator

from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from support import SEGMENTS

from zapp_atlas.api.authz import require_current_identity
from zapp_atlas.api.layout import LEVELS, layout
from zapp_atlas.api.resources import PATH_PARAMETERS
from zapp_atlas.schema import pydantic_crud as models

# Routes for the classes the layout lists as standalone, and the lookups.
OUTSIDE_THE_TREE = ("/api/research-groups", "/api/chemicals", "/api/zfin")

# POSTs that change nothing: each is a lookup that takes a body only because
# what it looks up does not fit in a query string.
READS_SENT_AS_POST = {
    ("POST", "/api/chemicals/normalize"),
    ("POST", "/api/zfin/resolve"),
}


def _api_routes(client: TestClient) -> dict[tuple[str, str], APIRoute]:
    return {
        (method, route.path): route
        for route in client.app.routes
        if isinstance(route, APIRoute) and route.path.startswith("/api/")
        for method in route.methods
    }


def _item(level: str) -> str:
    return f"/api/{SEGMENTS[level]}/{{{PATH_PARAMETERS[level]}}}"


def _collection(level: str) -> str:
    parent = layout().levels[level].parent
    if parent is None:
        return f"/api/{SEGMENTS[level]}"
    return f"{_item(parent.name)}/{SEGMENTS[level]}"


def test_every_level_has_its_routes_with_the_derived_models(client: TestClient) -> None:
    routes = _api_routes(client)
    for level in LEVELS:
        body = getattr(models, f"{level}Input")
        read = getattr(models, f"{level}Read")

        create = routes["POST", _collection(level)]
        replace = routes["PUT", _item(level)]
        assert issubclass(create.body_field.field_info.annotation, body), level
        assert replace.body_field.field_info.annotation is body, level
        assert create.response_model is read, level
        assert replace.response_model is read, level

        assert ("DELETE", _item(level)) in routes, level
        fetch = routes["GET", _item(level)]
        # An image is fetched as the file itself.
        assert fetch.response_model is (None if level == "Image" else read), level


def test_the_tree_has_no_write_routes_but_those(client: TestClient) -> None:
    expected = {
        (method, path)
        for level in LEVELS
        for method, path in (
            ("POST", _collection(level)),
            ("PUT", _item(level)),
            ("DELETE", _item(level)),
        )
    }
    writes = {
        (method, path)
        for method, path in _api_routes(client)
        if method != "GET" and not path.startswith(OUTSIDE_THE_TREE)
    }
    assert writes == expected


def _calls(dependant: Dependant) -> Iterator[object]:
    yield dependant.call
    for dependency in dependant.dependencies:
        yield from _calls(dependency)


def test_every_write_requires_a_signed_in_caller(client: TestClient) -> None:
    """A new write route fails here until it is gated."""
    ungated = {
        key
        for key, route in _api_routes(client).items()
        if key[0] != "GET"
        and key not in READS_SENT_AS_POST
        and require_current_identity not in _calls(route.dependant)
    }
    assert ungated == set()
