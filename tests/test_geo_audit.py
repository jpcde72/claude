import json

from app.models import GeoAuditStatus
from app.services.geo.audit_service import (
    build_scorecard,
    parse_list,
    parse_terms,
    run_audit,
    run_diagnostic,
)
from app.services.geo.providers import MockProvider, get_provider


def test_parse_terms_mixed_separators_dedupes_and_preserves_order():
    raw = "best tents, acme reviews\nbest tents\n tent comparison "
    assert parse_terms(raw) == ["best tents", "acme reviews", "tent comparison"]


def test_parse_list():
    assert parse_list(" TrailPro, Summit Gear ,TrailPro") == ["TrailPro", "Summit Gear"]
    assert parse_list(None) == []


def test_factory_falls_back_to_mock_without_keys(monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    monkeypatch.setattr(settings, "SERPAPI_API_KEY", "")
    for surface in ("gemini", "ai_mode", "ai_overview"):
        provider = get_provider(surface, "Acme", "acme.com", ["TrailPro"])
        assert isinstance(provider, MockProvider)


def test_mock_provider_is_deterministic():
    p = MockProvider("gemini", "Acme", "acme.com", ["TrailPro"])
    r1, r2 = p.query("best tents"), p.query("best tents")
    assert r1.text == r2.text
    assert r1.provider_mode == "mock"
    assert r1.citations


def test_run_diagnostic_covers_all_surfaces_and_terms():
    analyses = run_diagnostic(
        brand="Acme",
        terms=["best tents", "acme reviews", "tent comparison"],
        surfaces=["gemini", "ai_overview"],
        brand_domain="acme.com",
        competitors=["TrailPro"],
    )
    assert len(analyses) == 6
    assert {a.surface for a in analyses} == {"gemini", "ai_overview"}


def test_scorecard_shape():
    analyses = run_diagnostic(
        brand="Acme", terms=["best tents", "acme reviews"],
        surfaces=["gemini"], brand_domain="acme.com",
    )
    scorecard = build_scorecard(analyses)
    assert set(scorecard) == {"overall", "surfaces"}
    overall = scorecard["overall"]
    assert overall["queries"] == 2
    assert 0.0 <= overall["presence_rate"] <= 1.0
    assert 0.0 <= overall["citation_rate"] <= 1.0
    assert "sentiment_breakdown" in overall


def test_run_audit_persists_results_scorecard_and_insights(db_session):
    audit = run_audit(
        db_session,
        brand="Acme Outdoor",
        terms_raw="best 2 person tent\nacme outdoor reviews\nbuy hiking tent",
        surfaces=["gemini", "ai_mode", "ai_overview"],
        brand_domain="acmeoutdoor.com",
        competitors_raw="TrailPro, Summit Gear",
    )
    assert audit.status == GeoAuditStatus.COMPLETED
    assert audit.data_mode == "mock"
    assert len(audit.results) == 9
    scorecard = json.loads(audit.scorecard_json)
    assert set(scorecard["surfaces"]) == {"gemini", "ai_mode", "ai_overview"}
    insights = json.loads(audit.insights_json)
    assert isinstance(insights, list)
    for rec in insights:
        assert {"pillar", "track", "priority", "finding", "action"} <= set(rec)


def test_run_audit_validates_inputs(db_session):
    import pytest

    with pytest.raises(ValueError):
        run_audit(db_session, brand="", terms_raw="x", surfaces=["gemini"])
    with pytest.raises(ValueError):
        run_audit(db_session, brand="Acme", terms_raw="", surfaces=["gemini"])
