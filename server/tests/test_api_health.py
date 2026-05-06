from fastapi.testclient import TestClient

from zapp_atlas.main import create_app


def test_health():
    client = TestClient(create_app())
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
