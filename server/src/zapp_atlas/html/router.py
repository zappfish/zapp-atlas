from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse


router = APIRouter(tags=["html"])


def _escape(value: str | None) -> str:
    if not value:
        return ""
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(auth_id: str | None = Query(default=None)) -> HTMLResponse:
    status_attrs = ""
    if auth_id:
        status_attrs = (
            f' hx-get="/auth/orcid/status/{_escape(auth_id)}"'
            ' hx-trigger="load"'
            ' hx-swap="innerHTML"'
        )

    return HTMLResponse(
        f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ZAPP Atlas ORCID Login</title>
    <script src="https://unpkg.com/htmx.org@2.0.4"></script>
  </head>
  <body>
    <main>
      <h1>ZAPP Atlas ORCID Login</h1>
      <p>Use ORCID to confirm an authenticated researcher identity for this server.</p>
      <p><a href="/auth/orcid/login">Sign in with ORCID</a></p>
      <section id="orcid-status"{status_attrs}></section>
    </main>
  </body>
</html>"""
    )

