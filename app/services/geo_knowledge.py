"""Loads the canonical GEO/AXO knowledge model shared with the geo-axo-strategist skill."""

import json
import re
from functools import lru_cache
from pathlib import Path

import markdown as md
from markupsafe import Markup

SKILL_DIR = Path(__file__).resolve().parents[2] / "skills" / "geo-axo-strategist"
KNOWLEDGE_PATH = SKILL_DIR / "assets" / "knowledge.json"
OUTLOOK_PATH = SKILL_DIR / "references" / "predictions-2027.md"
PLAYBOOK_PATH = SKILL_DIR / "references" / "playbook.md"

_UNSAFE_HREF = re.compile(r'(href|src)\s*=\s*"\s*(javascript|data|vbscript):[^"]*"', re.I)


@lru_cache
def load_knowledge() -> dict:
    return json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8"))


@lru_cache
def load_doc(name: str) -> str:
    path = {"outlook": OUTLOOK_PATH, "playbook": PLAYBOOK_PATH}[name]
    return path.read_text(encoding="utf-8")


def render_markdown(text: str) -> Markup:
    """Render markdown from users or the model without letting raw HTML through."""
    escaped = (text or "").replace("<", "&lt;")
    html = md.markdown(escaped, extensions=["tables", "fenced_code", "sane_lists"])
    return Markup(_UNSAFE_HREF.sub(r'\1="#"', html))


def ari_score(scores: dict[str, int]) -> int | None:
    """Weighted Agent Readiness Index v2; None until every component is scored."""
    components = load_knowledge()["ari"]["components"]
    if not scores or any(c["id"] not in scores for c in components):
        return None
    total = sum(c["weight"] * scores[c["id"]] for c in components)
    return round(total / sum(c["weight"] for c in components))


def ari_band(score: int | None) -> str:
    if score is None:
        return "Not yet scored"
    for band in load_knowledge()["ari"]["bands"]:
        if band["min"] <= score <= band["max"]:
            return band["label"]
    return ""


def knowledge_digest() -> str:
    """Compact, deterministic text form of the model for the LLM system prompt (cache-stable)."""
    return json.dumps(load_knowledge(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
