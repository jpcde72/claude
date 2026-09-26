import json
import os
import tempfile

os.environ.setdefault("INTENT_PLANNER_DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/geo_test.db")

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import geo_llm
from app.services.geo_knowledge import ari_band, ari_score, load_knowledge, render_markdown


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _new_project(client, name="Northwind Coffee") -> int:
    r = client.post("/geo/projects", data={"name": name, "sector": "FMCG", "market": "UK"}, follow_redirects=False)
    assert r.status_code == 303
    return int(r.headers["location"].rsplit("/", 1)[1])


def _events(text: str) -> list[dict]:
    return [json.loads(line[6:]) for line in text.split("\n\n") if line.startswith("data: ")]


def test_knowledge_model_is_consistent():
    kb = load_knowledge()
    assert sum(c["weight"] for c in kb["ari"]["components"]) == 100
    ids = {w["id"] for w in kb["workstreams"]}
    assert {f"W{i}" for i in range(1, 21)} <= ids
    for a in kb["actions"]:
        assert set(a["workstreams"]) <= ids, a["id"]
    assert all(p["confidence"] in {"high", "medium", "low"} for p in kb["predictions"])


def test_ari_scoring():
    scores = {c["id"]: 100 for c in load_knowledge()["ari"]["components"]}
    assert ari_score(scores) == 100
    assert ari_band(100) == "Agent-native"
    del scores["mandate"]
    assert ari_score(scores) is None
    assert ari_band(None) == "Not yet scored"


def test_markdown_is_sanitised():
    html = str(render_markdown("<script>x()</script> [a](javascript:alert(1)) **ok**"))
    assert "<script" not in html and "javascript:" not in html and "<strong>ok</strong>" in html


@pytest.mark.parametrize("path", ["/geo", "/geo/knowledge", "/geo/knowledge/outlook", "/geo/knowledge/playbook", "/geo/knowledge.json"])
def test_pages_render(client, path):
    assert client.get(path).status_code == 200


def test_brand_cookie_selects_system(client):
    client.cookies.set("geo_brand", "om")
    assert 'data-brand="om"' in client.get("/geo").text
    client.cookies.set("geo_brand", "bogus")
    assert 'data-brand="jp"' in client.get("/geo").text
    client.cookies.clear()


def test_project_ari_and_asset_versioning(client):
    pid = _new_project(client)
    comps = [c["id"] for c in load_knowledge()["ari"]["components"]]
    client.post(f"/geo/projects/{pid}/ari", data={c: "70" for c in comps})
    assert ">70<" in client.get(f"/geo/projects/{pid}").text

    r = client.post(f"/geo/projects/{pid}/assets", data={"title": "Probe set", "kind": "probe_set", "content": "v1"}, follow_redirects=False)
    aid = int(r.headers["location"].rsplit("/", 1)[1])
    client.post(f"/geo/assets/{aid}/versions", data={"content": "v2", "change_note": "tightened"})
    client.post(f"/geo/assets/{aid}/restore/1")
    assets = client.get(f"/geo/projects/{pid}/assets.json").json()
    assert assets == [{"id": aid, "title": "Probe set", "kind": "probe_set", "version": 3}]
    assert "v1" in client.get(f"/geo/assets/{aid}?v=3").text
    assert "Probe set" in client.get(f"/geo/projects/{pid}/export.md").text


def test_ask_streams_persists_and_saves(client, monkeypatch):
    pid = _new_project(client, "Acme B2B")
    seen = {}

    async def fake_stream(req):
        seen["req"] = req
        yield {"type": "status", "message": "Searching the web…"}
        yield {"type": "text", "text": "## Answer\n"}
        yield {"type": "text", "text": "Do A1 first."}
        yield {"type": "final", "answer": "## Answer\nDo A1 first.", "model": "test-model"}

    monkeypatch.setattr(geo_llm, "stream_answer", fake_stream)
    r = client.post("/geo/ask", json={"question": "Where do we start?", "project_id": pid, "web_search": True})
    events = _events(r.text)
    assert [e["type"] for e in events] == ["status", "text", "text", "done"]
    assert seen["req"].project.name == "Acme B2B" and seen["req"].web_search

    ex_id = events[-1]["exchange_id"]
    saved = client.post(f"/geo/exchanges/{ex_id}/save", data={"project_id": pid, "title": "Start here", "kind": "action_plan"}).json()
    page = client.get(saved["url"]).text
    assert "Do A1 first." in page and "Start here" in page

    # Saving the same answer onto an existing asset creates its next version.
    aid = saved["asset_id"]
    client.post(f"/geo/exchanges/{ex_id}/save", data={"project_id": pid, "asset_id": aid})
    versions = client.get(f"/geo/projects/{pid}/assets.json").json()
    assert versions[0]["version"] == 2
    assert "Where do we start?" in client.get(f"/geo/projects/{pid}").text


def test_ask_rejects_empty_question(client):
    assert client.post("/geo/ask", json={"question": "  "}).status_code == 422


def test_system_prompt_caches_stable_prefix():
    kb_project = type("P", (), {"name": "X", "sector": None, "market": None, "segment": "b2b", "website": None,
                                "competitors": None, "notes": None, "ari": {}})()
    req = geo_llm.AskRequest("q", project=kb_project)
    blocks = geo_llm.system_blocks(req)
    assert blocks[0]["cache_control"] == {"type": "ephemeral"}
    assert "<knowledge_model>" in blocks[0]["text"] and "X" not in blocks[0]["text"].split("</playbook>")[-1]
    assert "<brand_project>" in blocks[1]["text"]
    assert geo_llm.system_blocks(geo_llm.AskRequest("q"))[0]["text"] == blocks[0]["text"]
