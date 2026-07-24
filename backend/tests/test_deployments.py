import pytest

from backend import app as app_module
from backend.lib.index_elastic import es_client


def _entry(clip: str, n_chunks: int) -> dict:
    ids = [f"{clip}__scene__{i:03d}" for i in range(n_chunks)]
    return {
        "key": f"{clip}.mp4:1:1",
        "source": f"/library/{clip}.mp4",
        "chunk_ids": ids,
        "chunk_paths": {cid: f"/chunks/{cid}.mp4" for cid in ids},
    }


class FakeES:
    """Pretends only `present_ids` exist in the index."""

    def __init__(self, present_ids: set):
        self.present_ids = present_ids

    def search(self, index=None, query=None, size=None, source=None, **kw):
        wanted = query["ids"]["values"]
        return {
            "hits": {
                "hits": [{"_id": i} for i in wanted if i in self.present_ids]
            }
        }


def test_reconcile_requeues_missing_clips(monkeypatch):
    manifest = {"a.mp4": _entry("a", 2), "b.mp4": _entry("b", 2)}
    present = {"a__scene__000", "a__scene__001"}  # only clip a is indexed
    monkeypatch.setattr(app_module, "es", FakeES(present))
    app_module._reconcile_manifest(manifest)
    assert list(manifest) == ["a.mp4"]


def test_reconcile_requeues_partially_indexed_clip(monkeypatch):
    manifest = {"a.mp4": _entry("a", 3)}
    present = {"a__scene__000", "a__scene__001"}  # scene 002 missing
    monkeypatch.setattr(app_module, "es", FakeES(present))
    app_module._reconcile_manifest(manifest)
    assert manifest == {}


def test_reconcile_keeps_everything_when_index_matches(monkeypatch):
    manifest = {"a.mp4": _entry("a", 2)}
    monkeypatch.setattr(
        app_module, "es", FakeES({"a__scene__000", "a__scene__001"})
    )
    app_module._reconcile_manifest(manifest)
    assert list(manifest) == ["a.mp4"]


def test_reconcile_empty_manifest_is_noop(monkeypatch):
    class ExplodingES:
        def search(self, **kw):
            raise AssertionError("should not query ES for an empty manifest")

    monkeypatch.setattr(app_module, "es", ExplodingES())
    app_module._reconcile_manifest({})


def test_es_client_requires_config(monkeypatch):
    monkeypatch.delenv("ES_URL", raising=False)
    monkeypatch.delenv("ES_CLOUD_ID", raising=False)
    with pytest.raises(RuntimeError, match="No Elasticsearch configured"):
        es_client()
