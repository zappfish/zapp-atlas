from __future__ import annotations

"""The 'a chemical must be identifiable' rule is declared in the schema, but
LinkML's pydanticgen does not turn class-level rules into validators, so it is
enforced by a guard in ``_stressor_from_create``. Lock that guard in."""

import pytest

from zapp_atlas.api.services.studies import _stressor_from_create
from zapp_atlas.schema.pydantic_crud import StressorChemicalCreate


def test_stressor_must_have_chemical_id_or_unrecognized_name() -> None:
    # Neither identifier present -> rejected.
    with pytest.raises(ValueError):
        _stressor_from_create(None, StressorChemicalCreate())

    # The free-text fallback alone is enough to be valid.
    stressor = _stressor_from_create(
        None, StressorChemicalCreate(unrecognized_chemical_name="weird compound X")
    )
    assert stressor.unrecognized_chemical_name == "weird compound X"
