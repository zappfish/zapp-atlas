"""Shared Jinja2 environment.

Every HTML response in the app — pages, HTMX partials, and error pages —
renders through the single `templates` object defined here, so that all
user-visible markup lives under `html/templates/` and can be edited without
touching Python.
"""

from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from zapp_atlas.api.deps import open_session
from zapp_atlas.auth.services import ORCID_AUTH_COOKIE, get_orcid_identity

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def _current_identity(request: Request) -> dict[str, object]:
    """Expose the signed-in identity to every template as `current_identity`,
    so the shared header can show a user chip without each route passing it.
    """
    identity_id = request.cookies.get(ORCID_AUTH_COOKIE)
    if not identity_id:
        return {"current_identity": None}
    with open_session(request) as session:
        return {"current_identity": get_orcid_identity(session, identity_id)}


templates = Jinja2Templates(
    directory=TEMPLATES_DIR,
    context_processors=[_current_identity],
)
