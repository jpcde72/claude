---
name: geo-audit
description: >
  Run the GEO (Generative Engine Optimization) diagnostic: query Google
  Gemini, AI Mode, and AI Overviews for a set of terms, measure brand
  presence, citation, and sentiment, then turn the findings into strategic
  recommendations (content, technical, PDP, scripting) organized by the
  trust architecture. Use when the user asks for a GEO audit, AI visibility
  check, brand presence in AI answers, or citation/sentiment analysis.
---

# GEO Audit — Diagnostic Phase

You are running the diagnostic part of a GEO audit. The goal is to measure
how generative engines currently treat a brand, then convert those
measurements into a prioritized action plan.

## 1. Gather inputs

Collect from the user (ask only for what's missing):

- **Brand name** (required) and **brand domain** (strongly recommended —
  citation detection needs it)
- **Terms** (required): 5–20 queries spanning the funnel — category terms,
  "best/vs/review" transactional terms, and brand-navigational terms
- **Competitors**: 2–5 names for share-of-voice analysis
- **Surfaces**: default to all three (`gemini`, `ai_mode`, `ai_overview`)

## 2. Run the diagnostic

From the repository root:

```bash
python -m app.geo_cli \
  --brand "BRAND" --domain BRAND-DOMAIN \
  --terms "term one, term two" \
  --competitors "Comp A, Comp B" \
  --format markdown --output geo-report.md
```

Add `--format json` when you need to post-process results. The same
pipeline is available as an HTTP API (`POST /api/geo/audits`) and in the
web UI at `/geo` when the app is running.

**Credentials:** live data requires `GEMINI_API_KEY` (Gemini surface) and
`SERPAPI_API_KEY` (AI Mode + AI Overviews). Without keys the run falls
back to deterministic mock data and the report is stamped
`data_mode: mock` — always tell the user when results are simulated and
never present mock numbers as market findings.

## 3. Interpret the scorecard

- **Presence rate** — share of answers that mention the brand at all.
- **Citation rate** — share of answers grounding on the brand's own domain.
  Presence without citation means engines describe the brand from
  third-party sources the brand doesn't control.
- **Prominence** — how early the brand appears in the answer (earlier =
  stronger association).
- **Sentiment** (−1..+1) — framing around brand mentions.
- **Share of voice** — brand mentions vs. competitor mentions.
- Compare surfaces: AI Overviews reward classic organic strength; Gemini
  and AI Mode reward grounded, machine-readable, entity-consistent content.

## 4. Deliver strategy through the trust architecture

The report's insights are organized by five trust pillars — keep this
framing in the deliverable:

1. **Entity Clarity & Consistency** — engines can resolve who the brand is
2. **Authority & Corroboration** — third parties independently confirm it
3. **Evidence & Verifiability** — machine-readable proof to ground answers on
4. **Experience & Depth** — content that resolves queries better than incumbents
5. **Reputation & Sentiment** — objections answered, criticism addressed

Each recommendation is routed to a delivery track: **content** (pages to
create/reshape), **technical** (crawlability, rendering, Google-Extended
access, llms.txt), **pdp** (product detail page upgrades), **scripting**
(JSON-LD to deploy — the report includes starter snippets; adapt the
REPLACE placeholders before shipping).

When presenting to the user: lead with the 2–3 highest-leverage findings
in plain language, then the scorecard, then the prioritized backlog
(P0 → P2) grouped by track. Quote the per-term evidence strings when a
finding needs proof.
