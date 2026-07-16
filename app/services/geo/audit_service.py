"""GEO audit orchestration: run surfaces x terms, score, persist, advise."""
from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import GeoAudit, GeoAuditStatus, GeoQueryResult, GeoSurface
from app.services.geo.analysis import TermAnalysis, analyze_response
from app.services.geo.insights import generate_insights
from app.services.geo.providers import get_provider

ALL_SURFACES = [s.value for s in GeoSurface]


def parse_terms(raw: str) -> list[str]:
    """Split a newline/comma separated term list, preserving order."""
    parts = [p.strip() for chunk in raw.splitlines() for p in chunk.split(",")]
    return list(dict.fromkeys(p for p in parts if p))


def parse_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    return list(dict.fromkeys(p.strip() for p in raw.split(",") if p.strip()))


def run_diagnostic(
    brand: str,
    terms: list[str],
    surfaces: list[str],
    brand_domain: str = "",
    competitors: list[str] | None = None,
) -> list[TermAnalysis]:
    """Query every surface for every term and analyze the answers (no DB)."""
    competitors = competitors or []
    analyses: list[TermAnalysis] = []
    for surface in surfaces:
        provider = get_provider(surface, brand, brand_domain, competitors)
        for term in terms:
            response = provider.query(term)
            analyses.append(
                analyze_response(response, brand, brand_domain, competitors)
            )
    return analyses


def build_scorecard(analyses: list[TermAnalysis]) -> dict:
    """Aggregate per-surface and overall presence/citation/sentiment metrics."""

    def _bucket(rows: list[TermAnalysis]) -> dict:
        answered = [r for r in rows if r.answered and r.error is None]
        mentioned = [r for r in answered if r.mentioned]
        n = len(answered)
        return {
            "queries": len(rows),
            "answered": n,
            "errors": sum(1 for r in rows if r.error),
            "presence_rate": round(len(mentioned) / n, 3) if n else 0.0,
            "citation_rate": round(
                sum(1 for r in answered if r.cited) / n, 3
            ) if n else 0.0,
            "avg_prominence": round(
                sum(r.prominence for r in mentioned) / len(mentioned), 3
            ) if mentioned else 0.0,
            "avg_sentiment": round(
                sum(r.sentiment_score for r in mentioned) / len(mentioned), 3
            ) if mentioned else 0.0,
            "share_of_voice": round(
                sum(r.share_of_voice for r in answered) / n, 3
            ) if n else 0.0,
            "sentiment_breakdown": {
                label: sum(1 for r in answered if r.sentiment_label == label)
                for label in ("positive", "neutral", "mixed", "negative", "not_mentioned")
            },
        }

    surfaces = sorted({a.surface for a in analyses})
    return {
        "overall": _bucket(analyses),
        "surfaces": {s: _bucket([a for a in analyses if a.surface == s]) for s in surfaces},
    }


def data_mode(analyses: list[TermAnalysis]) -> str:
    modes = {a.provider_mode for a in analyses}
    if modes == {"live"}:
        return "live"
    if modes == {"mock"}:
        return "mock"
    return "mixed"


def run_audit(
    db: Session,
    brand: str,
    terms_raw: str,
    surfaces: list[str],
    brand_domain: str = "",
    competitors_raw: str = "",
) -> GeoAudit:
    """Run a full diagnostic audit and persist results + scorecard + insights."""
    terms = parse_terms(terms_raw)
    competitors = parse_list(competitors_raw)
    surfaces = [s for s in surfaces if s in ALL_SURFACES] or ALL_SURFACES
    if not brand.strip():
        raise ValueError("brand is required")
    if not terms:
        raise ValueError("at least one term is required")

    audit = GeoAudit(
        brand=brand.strip(),
        brand_domain=brand_domain.strip() or None,
        competitors=", ".join(competitors) or None,
        terms="\n".join(terms),
        surfaces=",".join(surfaces),
        status=GeoAuditStatus.RUNNING,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)

    try:
        analyses = run_diagnostic(
            brand=audit.brand,
            terms=terms,
            surfaces=surfaces,
            brand_domain=brand_domain.strip(),
            competitors=competitors,
        )
        for a in analyses:
            db.add(GeoQueryResult(
                audit_id=audit.id,
                term=a.term,
                surface=GeoSurface(a.surface),
                provider_mode=a.provider_mode,
                response_text=a.evidence or None,
                mentioned=a.mentioned,
                mention_count=a.mention_count,
                prominence=a.prominence,
                cited=a.cited,
                citations_json=json.dumps(a.citations),
                competitor_mentions_json=json.dumps(a.competitor_mentions),
                sentiment_score=a.sentiment_score,
                sentiment_label=a.sentiment_label,
                error=a.error,
            ))

        scorecard = build_scorecard(analyses)
        insights = generate_insights(
            analyses, audit.brand, brand_domain.strip(), competitors
        )
        audit.scorecard_json = json.dumps(scorecard)
        audit.insights_json = json.dumps([r.to_dict() for r in insights])
        audit.data_mode = data_mode(analyses)
        audit.status = GeoAuditStatus.COMPLETED
        audit.completed_at = datetime.utcnow()
        db.commit()
    except Exception as exc:  # noqa: BLE001 - surface any provider failure on the audit row
        db.rollback()
        audit.status = GeoAuditStatus.FAILED
        audit.error = str(exc)
        db.commit()
    db.refresh(audit)
    return audit


def audit_report(audit: GeoAudit) -> dict:
    """JSON-serializable view of a persisted audit."""
    return {
        "id": audit.id,
        "brand": audit.brand,
        "brand_domain": audit.brand_domain,
        "competitors": parse_list(audit.competitors),
        "terms": audit.terms.splitlines(),
        "surfaces": audit.surfaces.split(","),
        "status": audit.status.value,
        "data_mode": audit.data_mode,
        "created_at": audit.created_at.isoformat() if audit.created_at else None,
        "completed_at": audit.completed_at.isoformat() if audit.completed_at else None,
        "error": audit.error,
        "scorecard": json.loads(audit.scorecard_json) if audit.scorecard_json else None,
        "insights": json.loads(audit.insights_json) if audit.insights_json else [],
        "results": [
            {
                "term": r.term,
                "surface": r.surface.value,
                "provider_mode": r.provider_mode,
                "mentioned": r.mentioned,
                "mention_count": r.mention_count,
                "prominence": r.prominence,
                "cited": r.cited,
                "citations": json.loads(r.citations_json) if r.citations_json else [],
                "competitor_mentions": (
                    json.loads(r.competitor_mentions_json)
                    if r.competitor_mentions_json else {}
                ),
                "sentiment_score": r.sentiment_score,
                "sentiment_label": r.sentiment_label,
                "evidence": r.response_text,
                "error": r.error,
            }
            for r in audit.results
        ],
    }
