"""Regression gate: every SQLAlchemy model must import and map cleanly.

A model that inherits the declarative ``Base`` without a ``__tablename__``
(or carries a malformed relationship) raises at import / configure time.
Because ``conftest`` imports the model chain, such a break takes down the
*entire* suite at collection, so this test is the canary that names the
failure explicitly.

Regression: PR #117 added ``ResearchGroup`` / ``ResearchGroupMember``
without ``__tablename__``, breaking ``uv run pytest`` at conftest import.
"""

import importlib

from sqlalchemy.orm import configure_mappers


def test_models_import_and_configure():
    # Importing ``db`` pulls in the generated schema ``Base`` plus the auth
    # models for their mapper-registration side effects.
    importlib.import_module("zapp_atlas.db")
    importlib.import_module("zapp_atlas.auth.models")
    # Resolves every mapper and relationship; raises on any misconfiguration
    # (missing table, unresolvable foreign_keys, ambiguous join, ...).
    configure_mappers()


def test_every_mapped_class_has_a_table():
    importlib.import_module("zapp_atlas.auth.models")
    from zapp_atlas.schema._gen.sqla import Base

    missing = [
        mapper.class_.__name__
        for mapper in Base.registry.mappers
        if not getattr(mapper.class_, "__tablename__", None)
    ]
    assert not missing, f"models missing __tablename__: {missing}"
