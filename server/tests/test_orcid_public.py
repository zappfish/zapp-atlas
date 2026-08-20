"""Unit tests for the best-effort ORCID public API name lookup (#142)."""

from __future__ import annotations

import io
import json
from contextlib import contextmanager
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from zapp_atlas.auth.orcid_public import fetch_public_name

CARBERRY = "0000-0002-1825-0097"


@contextmanager
def _response(payload: dict) -> io.BytesIO:
    yield io.BytesIO(json.dumps(payload).encode("utf-8"))


def _personal_details(
    given: str | None = None, family: str | None = None, credit: str | None = None
) -> dict:
    def value(v: str | None) -> dict | None:
        return {"value": v} if v is not None else None

    return {
        "name": {
            "given-names": value(given),
            "family-name": value(family),
            "credit-name": value(credit),
        }
    }


def test_prefers_the_credit_name() -> None:
    payload = _personal_details(given="Josiah", family="Carberry", credit="J. S. Carberry")
    with patch("zapp_atlas.auth.orcid_public.urlopen", return_value=_response(payload)) as urlopen:
        name = fetch_public_name(CARBERRY)

    assert name == "J. S. Carberry"
    (request,), _ = urlopen.call_args
    assert request.full_url == f"https://pub.orcid.org/v3.0/{CARBERRY}/personal-details"


def test_falls_back_to_given_and_family_names() -> None:
    payload = _personal_details(given="Josiah", family="Carberry")
    with patch("zapp_atlas.auth.orcid_public.urlopen", return_value=_response(payload)):
        assert fetch_public_name(CARBERRY) == "Josiah Carberry"


def test_uses_given_name_alone_when_family_name_is_withheld() -> None:
    payload = _personal_details(given="Josiah")
    with patch("zapp_atlas.auth.orcid_public.urlopen", return_value=_response(payload)):
        assert fetch_public_name(CARBERRY) == "Josiah"


def test_private_record_yields_none() -> None:
    with patch("zapp_atlas.auth.orcid_public.urlopen", return_value=_response({"name": None})):
        assert fetch_public_name(CARBERRY) is None


def test_http_error_yields_none() -> None:
    error = HTTPError(url="...", code=404, msg="Not Found", hdrs=None, fp=None)
    with patch("zapp_atlas.auth.orcid_public.urlopen", side_effect=error):
        assert fetch_public_name(CARBERRY) is None


def test_network_error_yields_none() -> None:
    with patch("zapp_atlas.auth.orcid_public.urlopen", side_effect=URLError("no route")):
        assert fetch_public_name(CARBERRY) is None


def test_malformed_body_yields_none() -> None:
    @contextmanager
    def garbage():
        yield io.BytesIO(b"<html>not json</html>")

    with patch("zapp_atlas.auth.orcid_public.urlopen", return_value=garbage()):
        assert fetch_public_name(CARBERRY) is None
