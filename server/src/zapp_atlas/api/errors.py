"""Domain errors that carry an HTTP meaning.

The service layer is HTTP-agnostic -- routers are what raise
``HTTPException``. But some rules are declared in the LinkML schema and have to
be re-checked deep in a service, well below the router, because ``pydanticgen``
does not turn class-level ``rules`` into validators. Those checks raise
:class:`SchemaRuleViolation`, and ``create_app`` maps it to 422 so a submitter
gets the same "your input was rejected" response FastAPI gives for any other
validation failure, rather than a 500.
"""

from __future__ import annotations


class SchemaRuleViolation(ValueError):
    """A schema-declared rule the generated validators cannot enforce."""
