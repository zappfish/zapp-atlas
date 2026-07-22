"""Shared Jinja2 environment.

Every HTML response in the app — pages, HTMX partials, and error pages —
renders through the single `templates` object defined here, so that all
user-visible markup lives under `html/templates/` and can be edited without
touching Python.
"""

from pathlib import Path

from fastapi.templating import Jinja2Templates


TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

templates = Jinja2Templates(directory=TEMPLATES_DIR)
