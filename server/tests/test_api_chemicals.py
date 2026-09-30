import json
import sqlite3

import httpx
import pytest

from zapp_atlas.chem import build_cache, normalize
from zapp_atlas.chem.cache import SCHEMA


def _norm(primary_id, label, equivs=()):
    return {
        "normalized": True,
        "primary_id": primary_id,
        "label": label,
        "description": f"{label} description",
        # NodeNorm's shape: a list of classes, most specific first.
        "biolink_type": ["biolink:SmallMolecule", "biolink:ChemicalEntity"],
        "equivalent_identifiers": [
            {"identifier": i, "label": label, "description": None} for i in (primary_id, *equivs)
        ],
    }


@pytest.fixture
def chem_cache(tmp_path):
    """A small cache built through the same functions as the real one."""
    normalized = tmp_path / "chebi_normalized.json"
    normalized.write_text(
        json.dumps(
            {
                "CHEBI:16236": _norm("CHEBI:16236", "ethanol", ["PUBCHEM.COMPOUND:702"]),
                "CHEBI:52092": _norm("CHEBI:16236", "ethanol"),  # a secondary id
                "CHEBI:28262": _norm("CHEBI:28262", "dimethyl sulfoxide"),
            }
        )
    )
    synonyms = tmp_path / "chebi_synonym_mapping.json"
    synonyms.write_text(
        json.dumps(
            {
                "ethyl alcohol": {"CHEBI:16236": "", "CHEBI:52092": ""},
                "<i>DMSO</i>": {"CHEBI:28262": ""},
            }
        )
    )
    path = tmp_path / "cache.db"
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    build_cache.build_chemicals(conn, normalized, resume=False, test_limit=None)
    build_cache.build_synonyms(conn, synonyms)
    conn.close()
    return path


@pytest.fixture
def chem_client(client, chem_cache):
    client.app.state.settings.chem_cache_path = chem_cache
    return client


@pytest.fixture
def no_cache(client, tmp_path):
    client.app.state.settings.chem_cache_path = tmp_path / "missing.db"
    return client


@pytest.fixture
def offline(monkeypatch):
    """Make every NodeNorm / Name Resolver call fail as if the network were down."""

    def fail(*args, **kwargs):
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(normalize, "normalize_curie", fail)
    monkeypatch.setattr(normalize, "resolve_name", fail)
    monkeypatch.setattr(normalize, "autocomplete", fail)


def test_autocomplete_groups_ids_under_a_name(chem_client):
    r = chem_client.get("/api/chemicals/autocomplete", params={"q": "ETHyl"})
    assert r.status_code == 200
    [hit] = r.json()
    assert hit["name"] == "ethyl alcohol"
    assert hit["chebi_ids"] == ["CHEBI:16236", "CHEBI:52092"]
    assert hit["normalized"]["primary_id"] == "CHEBI:16236"


def test_autocomplete_finds_primary_labels_and_strips_markup(chem_client):
    names = [h["name"] for h in chem_client.get("/api/chemicals/autocomplete?q=d").json()]
    assert names == []  # too short
    names = [h["name"] for h in chem_client.get("/api/chemicals/autocomplete?q=dm").json()]
    assert names == ["DMSO"]
    names = [h["name"] for h in chem_client.get("/api/chemicals/autocomplete?q=dimeth").json()]
    assert names == ["dimethyl sulfoxide"]


def test_autocomplete_respects_limit(chem_client):
    hits = chem_client.get("/api/chemicals/autocomplete?q=eth&limit=1").json()
    assert [h["name"] for h in hits] == ["ethanol"]
    # The limit caps names, not ids: the last name still gets all of its terms.
    assert hits[0]["chebi_ids"] == ["CHEBI:16236", "CHEBI:52092"]


def test_without_a_cache_or_the_network_lookups_find_nothing(no_cache, offline):
    client = no_cache
    assert client.get("/api/chemicals/autocomplete?q=ethanol").json() == []
    assert client.get("/api/chemicals/vehicle-info?meaning=CHEBI:16236").json() == {
        "found": False,
        "result": None,
    }
    r = client.post("/api/chemicals/normalize", json={"name": "ethanol"})
    assert r.status_code == 200
    assert r.json()["result"]["normalized"] is False


def test_vehicle_info_by_own_id_and_by_equivalent(chem_client, offline):
    body = chem_client.get("/api/chemicals/vehicle-info?meaning=CHEBI:16236").json()
    assert body["found"] is True
    assert body["result"]["label"] == "ethanol"

    body = chem_client.get("/api/chemicals/vehicle-info?meaning=PUBCHEM.COMPOUND:702").json()
    assert body["found"] is True
    assert body["result"]["primary_id"] == "CHEBI:16236"

    # A prefix of a known identifier is not a match.
    body = chem_client.get("/api/chemicals/vehicle-info?meaning=PUBCHEM.COMPOUND:70").json()
    assert body["found"] is False


def test_vehicle_info_needs_a_curie(chem_client):
    assert chem_client.get("/api/chemicals/vehicle-info?meaning=ethanol").status_code == 400


@pytest.mark.parametrize(
    "body",
    [{}, {"namespace": "CHEBI"}, {"chemical_id": "16236"}, {"name": "  "}],
)
def test_normalize_rejects_incomplete_requests(chem_client, body):
    assert chem_client.post("/api/chemicals/normalize", json=body).status_code == 422


def test_normalize_by_id_uses_nodenorm(chem_client, monkeypatch):
    calls = []

    def fake_normalize(curie):
        calls.append(curie)
        return _norm("CHEBI:16236", "ethanol (nodenorm)")

    monkeypatch.setattr(normalize, "normalize_curie", fake_normalize)
    r = chem_client.post(
        "/api/chemicals/normalize", json={"namespace": "CHEBI", "chemical_id": "16236"}
    )
    body = r.json()
    assert calls == ["CHEBI:16236"]
    assert body["source"] == "nodenorm"
    assert body["result"]["label"] == "ethanol (nodenorm)"
    assert body["results"] == [body["result"]]


def test_normalize_by_id_falls_back_to_the_cache(chem_client, offline):
    r = chem_client.post(
        "/api/chemicals/normalize", json={"namespace": "CHEBI", "chemical_id": "16236"}
    )
    body = r.json()
    assert body["source"] == "local_cache"
    assert body["result"]["label"] == "ethanol"


def test_normalize_by_name_falls_back_to_the_cache(chem_client, offline):
    body = chem_client.post("/api/chemicals/normalize", json={"name": "ethyl alcohol"}).json()
    assert body["source"] == "local_cache"
    assert body["result"]["primary_id"] == "CHEBI:16236"


def test_normalize_by_name_returns_every_candidate(chem_client, monkeypatch):
    candidates = [_norm("CHEBI:16236", "ethanol"), _norm("CHEBI:28262", "dimethyl sulfoxide")]
    monkeypatch.setattr(normalize, "resolve_name", lambda name, limit: candidates)
    body = chem_client.post("/api/chemicals/normalize", json={"name": "solvent"}).json()
    assert body["source"] == "nodenorm"
    assert [r["primary_id"] for r in body["results"]] == ["CHEBI:16236", "CHEBI:28262"]


def test_vehicle_meanings_come_from_the_enum():
    meanings = build_cache.vehicle_meanings()
    assert "UMLS:C0036774" in meanings  # BSA
    assert not any(m.startswith("CHEBI:") for m in meanings)


def test_without_a_cache_autocomplete_asks_the_name_resolver(no_cache, monkeypatch):
    hits = [
        {"curie": "CHEBI:33216", "label": "Bisphenol A"},
        {"curie": "MESH:C120941", "label": "bis(1,10-phenanthroline)rhodium(III)"},
        {"curie": "CHEBI:99999", "label": "Bisphenol A"},
    ]
    calls = []
    monkeypatch.setattr(
        normalize, "autocomplete", lambda q, limit: calls.append((q, limit)) or hits
    )
    body = no_cache.get("/api/chemicals/autocomplete?q=bisphen&limit=7").json()
    assert calls == [("bisphen", 7)]
    assert body == [
        {"name": "Bisphenol A", "chebi_ids": ["CHEBI:33216", "CHEBI:99999"], "normalized": None},
        {"name": "bis(1,10-phenanthroline)rhodium(III)", "chebi_ids": [], "normalized": None},
    ]


def test_autocomplete_prefers_the_cache(chem_client, monkeypatch):
    monkeypatch.setattr(normalize, "autocomplete", lambda q, limit: pytest.fail("used the API"))
    assert chem_client.get("/api/chemicals/autocomplete?q=ethyl").json()


def test_without_a_cache_vehicle_info_asks_nodenorm(no_cache, monkeypatch):
    monkeypatch.setattr(normalize, "normalize_curie", lambda curie: _norm(curie, "PBS"))
    body = no_cache.get("/api/chemicals/vehicle-info?meaning=PUBCHEM.COMPOUND:24978514").json()
    assert body["found"] is True
    assert body["result"]["primary_id"] == "PUBCHEM.COMPOUND:24978514"


def test_vehicle_info_asks_nodenorm_for_what_the_cache_lacks(chem_client, monkeypatch):
    monkeypatch.setattr(normalize, "normalize_curie", lambda curie: _norm(curie, "BSA"))
    body = chem_client.get("/api/chemicals/vehicle-info?meaning=UMLS:C0036774").json()
    assert body["result"]["label"] == "BSA"
