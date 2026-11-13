import sqlite3

import pytest

from zapp_atlas.labels import Labels


@pytest.fixture
def labels(tmp_path) -> Labels:
    path = tmp_path / "labels.db"
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE term (id TEXT PRIMARY KEY, label TEXT NOT NULL) WITHOUT ROWID")
        db.execute("INSERT INTO term VALUES ('CHEBI:15377', 'water')")
    db.close()
    return Labels(path)


def test_label(labels):
    assert labels.label("CHEBI:15377") == "water"
    assert labels.label("CHEBI:1") is None


def test_label_or_curie(labels):
    assert labels.label_or_curie("CHEBI:15377") == "water"
    assert labels.label_or_curie("CHEBI:1") == "CHEBI:1"


def test_without_a_table_every_term_falls_back(tmp_path):
    labels = Labels(tmp_path / "missing.db")
    assert labels.label("CHEBI:15377") is None
    assert labels.label_or_curie("CHEBI:15377") == "CHEBI:15377"
