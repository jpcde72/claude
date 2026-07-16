"""Headless GEO diagnostic runner.

Used by the /geo-audit skill and CI. Runs the same pipeline as the web UI
without touching the database, and emits JSON or a Markdown report.

Examples:
    python -m app.geo_cli --brand "Acme Outdoor" --domain acmeoutdoor.com \
        --terms "best 2-person tent, acme outdoor reviews" \
        --competitors "TrailPro, Summit Gear" --format markdown

    python -m app.geo_cli --brand Acme --terms-file terms.txt --format json
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from app.services.geo.audit_service import (
    ALL_SURFACES,
    build_scorecard,
    data_mode,
    parse_list,
    parse_terms,
    run_diagnostic,
)
from app.services.geo.insights import generate_insights


def _markdown_report(payload: dict) -> str:
    lines = [
        f"# GEO Diagnostic — {payload['brand']}",
        "",
        f"- Surfaces: {', '.join(payload['surfaces'])}",
        f"- Terms audited: {len(payload['terms'])}",
        f"- Data mode: **{payload['data_mode']}**"
        + (" ⚠️ simulated — configure API keys for live data"
           if payload["data_mode"] != "live" else ""),
        "",
        "## Scorecard",
        "",
        "| Surface | Answered | Presence | Cited | Prominence | Sentiment | Share of voice |",
        "|---|---|---|---|---|---|---|",
    ]
    scorecard = payload["scorecard"]
    rows = list(scorecard["surfaces"].items()) + [("overall", scorecard["overall"])]
    for name, s in rows:
        lines.append(
            f"| {name.replace('_', ' ')} | {s['answered']}/{s['queries']} "
            f"| {s['presence_rate']:.0%} | {s['citation_rate']:.0%} "
            f"| {s['avg_prominence']:.0%} | {s['avg_sentiment']:+.2f} "
            f"| {s['share_of_voice']:.0%} |"
        )

    lines += ["", "## Strategic insights (trust architecture)", ""]
    if not payload["insights"]:
        lines.append("_No rule-based findings — brand posture looks healthy on the audited terms._")
    for rec in payload["insights"]:
        lines += [
            f"### [{rec['priority']}] [{rec['track']}] {rec['title']}",
            f"*Pillar: {rec['pillar_label']}*",
            "",
            f"**Finding:** {rec['finding']}",
            "",
            f"**Action:** {rec['action']}",
        ]
        if rec["affected_terms"]:
            lines.append(f"**Terms:** {', '.join(rec['affected_terms'])}")
        if rec.get("snippet"):
            lines += ["", "```json", rec["snippet"], "```"]
        lines.append("")

    lines += [
        "## Per-term results",
        "",
        "| Term | Surface | Mentioned | Cited | Sentiment | Competitor mentions |",
        "|---|---|---|---|---|---|",
    ]
    for r in payload["results"]:
        comp = ", ".join(f"{k}×{v}" for k, v in r["competitor_mentions"].items()) or "—"
        mentioned = f"yes ×{r['mention_count']}" if r["mentioned"] else ("error" if r["error"] else "no")
        lines.append(
            f"| {r['term']} | {r['surface'].replace('_', ' ')} | {mentioned} "
            f"| {'yes' if r['cited'] else 'no'} | {r['sentiment_label']} | {comp} |"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a GEO audit diagnostic.")
    parser.add_argument("--brand", required=True)
    parser.add_argument("--domain", default="", help="Brand domain, e.g. acme.com")
    parser.add_argument("--terms", default="", help="Comma/newline separated terms")
    parser.add_argument("--terms-file", default="", help="File with one term per line")
    parser.add_argument("--competitors", default="", help="Comma-separated competitor names")
    parser.add_argument(
        "--surfaces", default=",".join(ALL_SURFACES),
        help=f"Comma-separated subset of: {', '.join(ALL_SURFACES)}",
    )
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", default="", help="Write report to this path instead of stdout")
    args = parser.parse_args(argv)

    raw_terms = args.terms
    if args.terms_file:
        raw_terms += "\n" + Path(args.terms_file).read_text()
    terms = parse_terms(raw_terms)
    if not terms:
        parser.error("no terms given — use --terms or --terms-file")

    surfaces = [s for s in parse_list(args.surfaces) if s in ALL_SURFACES]
    if not surfaces:
        parser.error(f"no valid surfaces — choose from: {', '.join(ALL_SURFACES)}")
    competitors = parse_list(args.competitors)

    analyses = run_diagnostic(
        brand=args.brand,
        terms=terms,
        surfaces=surfaces,
        brand_domain=args.domain,
        competitors=competitors,
    )
    payload = {
        "brand": args.brand,
        "brand_domain": args.domain,
        "competitors": competitors,
        "terms": terms,
        "surfaces": surfaces,
        "data_mode": data_mode(analyses),
        "scorecard": build_scorecard(analyses),
        "insights": [
            r.to_dict()
            for r in generate_insights(analyses, args.brand, args.domain, competitors)
        ],
        "results": [asdict(a) for a in analyses],
    }

    if args.format == "json":
        out = json.dumps(payload, indent=2)
    else:
        out = _markdown_report(payload)

    if args.output:
        Path(args.output).write_text(out)
        print(f"Report written to {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
