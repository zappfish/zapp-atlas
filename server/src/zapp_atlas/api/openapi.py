"""Write out the API's OpenAPI document, which the client's types are generated from.

FastAPI already describes every path, verb, request body and response. Saving
that description lets the client build its request and response types from the
server's own statement of its interface, so the two cannot drift.

    python -m zapp_atlas.api.openapi ../client/src/api/openapi.json
"""

import json
import sys
from pathlib import Path

from zapp_atlas.main import create_app
from zapp_atlas.settings import AppSettings

# JSON has no comments, so the notice every generated file carries goes in an
# extension field, which OpenAPI allows at the top level and tools ignore.
NOTICE = "GENERATED FILE. DO NOT EDIT. Regenerate with `just api-types`."


def openapi_document() -> str:
    """The OpenAPI document as text, the same on every machine."""
    # Settings come from nowhere but their defaults, so a developer's .env
    # cannot change what is written.
    app = create_app(AppSettings(_env_file=None))
    # Sorted, so the order does not depend on the order routes are registered
    # in; then the notice is put first, where a reader will see it.
    document = json.loads(json.dumps(app.openapi(), sort_keys=True))
    return json.dumps({"x-generated": NOTICE, **document}, indent=2) + "\n"


if __name__ == "__main__":
    Path(sys.argv[1]).write_text(openapi_document())
