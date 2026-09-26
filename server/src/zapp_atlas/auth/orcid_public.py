"""Best-effort name lookup against the ORCID public API.

Used to pre-populate ``OrcidIdentity`` when an admin adds a group member by
ORCID, so the member has a display name before they ever log in themselves
(#142). Failure is always an option here — no network, a private record, an
unknown ORCID — and callers get ``None`` rather than an exception; the member's
own login later stores the authoritative name.

The app reaches this through ``app.state.orcid_name_lookup`` so tests can
inject a stub instead of the network.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

PUBLIC_API_BASE = "https://pub.orcid.org/v3.0"
TIMEOUT_SECONDS = 10


def _value(section: dict[str, Any], key: str) -> str | None:
    field = section.get(key)
    if isinstance(field, dict):
        return field.get("value")
    return None


def fetch_public_name(orcid_id: str) -> str | None:
    """Return the public display name for a bare ORCID, or ``None``."""
    request = Request(
        f"{PUBLIC_API_BASE}/{orcid_id}/personal-details",
        headers={"Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            details = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, json.JSONDecodeError):
        # OSError covers HTTPError and socket timeouts; URLError covers DNS
        # and connection failures. None of them should break adding a member.
        return None

    name = details.get("name")
    if not isinstance(name, dict):
        return None
    credit = _value(name, "credit-name")
    if credit:
        return credit
    parts = [_value(name, "given-names"), _value(name, "family-name")]
    return " ".join(part for part in parts if part) or None
