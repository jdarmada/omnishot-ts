from fastapi.testclient import TestClient

from backend import app as app_module
from backend.lib.index_elastic import rrf_fuse

client = TestClient(app_module.app)


def hit(chunk_id: str, score: float = 1.0) -> dict:
    return {"chunk_id": chunk_id, "clip_id": chunk_id.split("__")[0], "_score": score}


# ---------------------------------------------------------------------------
# rrf_fuse
# ---------------------------------------------------------------------------

def test_fuse_agreement_outranks_single_list():
    knn = [hit("a__scene__000"), hit("b__scene__000")]
    bm25 = [hit("c__scene__000"), hit("b__scene__000")]
    fused = rrf_fuse([knn, bm25])
    # "b" appears in both lists → highest fused score despite never ranking first
    assert fused[0]["chunk_id"] == "b__scene__000"


def test_fuse_preserves_order_within_single_list():
    knn = [hit("a__scene__000"), hit("b__scene__000"), hit("c__scene__000")]
    fused = rrf_fuse([knn])
    assert [h["chunk_id"] for h in fused] == [
        "a__scene__000",
        "b__scene__000",
        "c__scene__000",
    ]


def test_fuse_scores_decrease_monotonically():
    fused = rrf_fuse([[hit("a"), hit("b")], [hit("b"), hit("c")]])
    scores = [h["_score"] for h in fused]
    assert scores == sorted(scores, reverse=True)


def test_fuse_empty_lists():
    assert rrf_fuse([[], []]) == []


# ---------------------------------------------------------------------------
# /api/search hybrid routing
# ---------------------------------------------------------------------------

def _payload_hit(clip: str) -> dict:
    return {
        "chunk_id": f"{clip}__scene__000",
        "clip_id": clip,
        "_score": 1.0,
        "duration": 2.0,
        "start_sec": 0.0,
        "end_sec": 2.0,
    }


def test_search_routes_to_hybrid(monkeypatch):
    calls = {}

    monkeypatch.setattr(
        app_module.jina, "embed", lambda *a, **kw: [[0.1] * 4]
    )
    monkeypatch.setattr(
        app_module,
        "hybrid_search",
        lambda *a, **kw: calls.setdefault("hybrid", True) and [_payload_hit("h")],
    )
    monkeypatch.setattr(
        app_module,
        "knn_search",
        lambda *a, **kw: calls.setdefault("knn", True) and [_payload_hit("k")],
    )

    r = client.post("/api/search", json={"query": "beach", "hybrid": True})
    assert r.status_code == 200
    assert r.json()["hybrid"] is True
    assert calls == {"hybrid": True}
    assert r.json()["hits"][0]["clip_id"] == "h"

    calls.clear()
    r = client.post("/api/search", json={"query": "beach"})
    assert r.status_code == 200
    assert r.json()["hybrid"] is False
    assert calls == {"knn": True}
