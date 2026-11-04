"""Guards for schema-declared rules, shared by the services that re-check them.

The schema declares these as class-level ``rules``, but LinkML's pydanticgen
does not turn class-level rules into validators, so every service whose class
carries one re-checks it here. ``other_not_listed`` is the escape hatch for a
value missing from a controlled vocabulary; without the matching free-text
name the row records no recoverable identity at all, which is what the rules
exist to prevent.
"""

from __future__ import annotations

from zapp_atlas.api.errors import SchemaRuleViolation

OTHER_NOT_LISTED = "other_not_listed"


def _enum_value(value: object) -> object:
    """The plain value of an enum member, or the value itself if it is not one."""
    return getattr(value, "value", value)


def check_escape_hatch(payload: object, choice_slot: str, name_slot: str, noun: str) -> None:
    if _enum_value(getattr(payload, choice_slot, None)) != OTHER_NOT_LISTED:
        return
    if not getattr(payload, name_slot, None):
        raise SchemaRuleViolation(
            f"{noun} is '{OTHER_NOT_LISTED}', so {name_slot} is required to record which one."
        )
