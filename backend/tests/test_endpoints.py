from fastapi.testclient import TestClient

from backend import app as app_module

client = TestClient(app_module.app)


class FakeES:
    def info(self):
        return {
            "cluster_name": "test-cluster",
            "version": {"number": "9.4.3", "build_flavor": "default"},
        }


def test_health_reports_es_and_deployment(monkeypatch):
    monkeypatch.setattr(app_module, "es", FakeES())
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["elasticsearch"] is True
    assert body["deployment"] == {
        "flavor": "default",
        "version": "9.4.3",
        "cluster": "test-cluster",
    }


def test_health_survives_es_down(monkeypatch):
    class ExplodingES:
        def info(self):
            raise ConnectionError("no cluster")

    monkeypatch.setattr(app_module, "es", ExplodingES())
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["elasticsearch"] is False
    assert body["deployment"] is None


def test_status_shape():
    r = client.get("/api/status")
    assert r.status_code == 200
    body = r.json()
    for key in ("clips", "chunks", "state", "watch_dir", "events"):
        assert key in body


def test_set_library_api_rejects_missing_path():
    r = client.post("/api/library", json={"path": "/definitely/not/a/real/path"})
    assert r.status_code == 404
