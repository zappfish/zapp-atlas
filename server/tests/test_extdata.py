import gzip
import json

import pytest
from fastapi.testclient import TestClient

from zapp_atlas.main import create_app
from zapp_atlas.settings import AppSettings

HASH = "0123456789abcdef"
ZP_JSON = b'{"graphs": []}'


def make_client(extdata_dir) -> TestClient:
    settings = AppSettings(skip_seed=True, extdata_dir=extdata_dir, _env_file=None)
    return TestClient(create_app(settings))


@pytest.fixture
def bundle(tmp_path):
    (tmp_path / "zp.json").write_bytes(ZP_JSON)
    (tmp_path / "zp.json.gz").write_bytes(gzip.compress(ZP_JSON))
    (tmp_path / "zfa.json").write_bytes(b"{}")
    (tmp_path / "zp.db").write_bytes(b"not for browsers")
    files = {name: {} for name in ("zp.json", "zp.json.gz", "zfa.json", "zp.db")}
    (tmp_path / "manifest.json").write_text(json.dumps({"hash": HASH, "files": files}))
    return tmp_path


def test_manifest_is_served_uncached(bundle):
    res = make_client(bundle).get("/extdata/manifest.json")
    assert res.status_code == 200
    assert res.json()["hash"] == HASH
    assert res.headers["cache-control"] == "no-cache"


def test_file_is_sent_gzipped_when_accepted(bundle):
    res = make_client(bundle).get(f"/extdata/{HASH}/zp.json", headers={"Accept-Encoding": "gzip"})
    assert res.status_code == 200
    assert res.headers["content-encoding"] == "gzip"
    assert res.headers["content-type"] == "application/json"
    assert "immutable" in res.headers["cache-control"]
    assert res.content == ZP_JSON  # httpx decodes it


def test_file_is_sent_plain_when_gzip_not_accepted(bundle):
    res = make_client(bundle).get(
        f"/extdata/{HASH}/zp.json", headers={"Accept-Encoding": "identity"}
    )
    assert res.status_code == 200
    assert "content-encoding" not in res.headers
    assert res.content == ZP_JSON


def test_file_without_gzipped_copy_is_sent_plain(bundle):
    res = make_client(bundle).get(f"/extdata/{HASH}/zfa.json", headers={"Accept-Encoding": "gzip"})
    assert res.status_code == 200
    assert "content-encoding" not in res.headers


@pytest.mark.parametrize(
    "path",
    [
        "/extdata/ffffffffffffffff/zp.json",  # another bundle's hash
        f"/extdata/{HASH}/zp.db",  # server-only
        f"/extdata/{HASH}/manifest.json",
        f"/extdata/{HASH}/..%2Fmanifest.json",
    ],
)
def test_other_paths_are_not_found(bundle, path):
    assert make_client(bundle).get(path).status_code == 404


def test_everything_is_not_found_without_a_bundle(tmp_path):
    client = make_client(tmp_path)
    assert client.get("/extdata/manifest.json").status_code == 404
    assert client.get(f"/extdata/{HASH}/zp.json").status_code == 404
