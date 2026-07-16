"""Strategic GEO insights derived from diagnostic results.

Findings are organized around a five-pillar trust architecture — the signals
generative engines use to decide whether a brand is safe to name, cite, and
recommend:

- consistency: Entity Clarity & Consistency — the engine can resolve who you
  are; your name, domain, and facts agree everywhere it looks.
- authority:   Authority & Corroboration — independent third parties mention
  and rank you, so the engine can safely repeat the claim.
- evidence:    Evidence & Verifiability — machine-readable proof (structured
  data, spec sheets, citable pages) that answers can be grounded in.
- experience:  Experience & Depth — answer-shaped content that actually
  resolves the query better than the current sources.
- reputation:  Reputation & Sentiment — the tone of what the engine reads
  about you; objections answered, criticism addressed.

Every recommendation is routed to a delivery track:

- content:   pages/articles to create or reshape
- technical: crawlability, rendering, site architecture work
- pdp:       product detail page changes
- scripting: structured-data / JSON-LD scripts to deploy
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field

from app.services.geo.analysis import TermAnalysis

TRUST_PILLARS = {
    "consistency": "Entity Clarity & Consistency",
    "authority": "Authority & Corroboration",
    "evidence": "Evidence & Verifiability",
    "experience": "Experience & Depth",
    "reputation": "Reputation & Sentiment",
}

TRACKS = ("content", "technical", "pdp", "scripting")

TRANSACTIONAL_MARKERS = (
    "buy", "best", "price", "pricing", "cheap", "cheapest", "deal", "deals",
    "vs", "versus", "review", "reviews", "top", "compare", "comparison",
    "alternative", "alternatives", "coupon", "discount",
)


@dataclass
class Recommendation:
    pillar: str                 # key into TRUST_PILLARS
    track: str                  # one of TRACKS
    priority: str               # P0 | P1 | P2
    title: str
    finding: str
    action: str
    affected_terms: list[str] = field(default_factory=list)
    snippet: str | None = None  # ready-to-adapt JSON-LD, when applicable

    def to_dict(self) -> dict:
        data = asdict(self)
        data["pillar_label"] = TRUST_PILLARS.get(self.pillar, self.pillar)
        return data


def _jsonld(payload: dict) -> str:
    return json.dumps({"@context": "https://schema.org", **payload}, indent=2)


def organization_snippet(brand: str, domain: str) -> str:
    return _jsonld({
        "@type": "Organization",
        "name": brand,
        "url": f"https://{domain}" if domain else "https://YOUR-DOMAIN",
        "logo": f"https://{domain or 'YOUR-DOMAIN'}/logo.png",
        "sameAs": [
            "https://en.wikipedia.org/wiki/REPLACE",
            "https://www.linkedin.com/company/REPLACE",
        ],
        "description": f"REPLACE: one-sentence factual description of {brand}.",
    })


def product_snippet(brand: str, domain: str) -> str:
    return _jsonld({
        "@type": "Product",
        "name": f"REPLACE: {brand} product name",
        "brand": {"@type": "Brand", "name": brand},
        "description": "REPLACE: spec-level factual description.",
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "REPLACE",
            "reviewCount": "REPLACE",
        },
        "offers": {
            "@type": "Offer",
            "price": "REPLACE",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
            "url": f"https://{domain or 'YOUR-DOMAIN'}/products/REPLACE",
        },
    })


def faq_snippet(brand: str, terms: list[str]) -> str:
    sample = terms[0] if terms else "your key query"
    return _jsonld({
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f"Is {brand} a good choice for {sample}?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "REPLACE: direct, factual, objection-addressing answer.",
                },
            }
        ],
    })


def _terms_by(analyses: list[TermAnalysis], predicate) -> list[str]:
    seen: list[str] = []
    for a in analyses:
        if predicate(a) and a.term not in seen:
            seen.append(a.term)
    return seen


def generate_insights(
    analyses: list[TermAnalysis],
    brand: str,
    brand_domain: str = "",
    competitors: list[str] | None = None,
) -> list[Recommendation]:
    """Rule-based diagnostic -> strategy mapping across the trust pillars."""
    recs: list[Recommendation] = []
    competitors = competitors or []
    answered = [a for a in analyses if a.answered and a.error is None]
    if not answered:
        return recs

    terms = list(dict.fromkeys(a.term for a in answered))
    by_term: dict[str, list[TermAnalysis]] = {}
    for a in answered:
        by_term.setdefault(a.term, []).append(a)

    # --- 1. Invisibility: terms where the brand never appears on any surface ---
    invisible = [t for t, rows in by_term.items() if not any(r.mentioned for r in rows)]
    if invisible:
        recs.append(Recommendation(
            pillar="experience",
            track="content",
            priority="P0",
            title="Close the visibility gap on invisible terms",
            finding=(
                f"{brand} is absent from every AI answer for {len(invisible)} of "
                f"{len(terms)} audited terms. Engines are answering these queries "
                f"entirely with other brands' material."
            ),
            action=(
                "Publish answer-shaped pages for each invisible term: lead with a "
                "direct 2–3 sentence answer, follow with comparison tables, specs, "
                "and FAQs. Target the sources currently cited for these queries "
                "with digital-PR outreach so third parties corroborate the page."
            ),
            affected_terms=invisible,
        ))
        recs.append(Recommendation(
            pillar="consistency",
            track="technical",
            priority="P1",
            title="Verify AI crawlers can reach and render the site",
            finding=(
                "Total absence across surfaces often has a technical root: pages "
                "blocked for Google-Extended, content rendered client-side only, "
                "or key facts locked inside images and PDFs."
            ),
            action=(
                "Confirm robots.txt does not block Google-Extended or Googlebot; "
                "ensure primary content is server-rendered HTML; expose key facts "
                "as crawlable text; add an llms.txt manifest pointing engines at "
                "canonical, citable pages."
            ),
            affected_terms=invisible,
        ))

    # --- 2. Mentioned but never cited: engine knows you, can't ground on you ---
    uncited = _terms_by(answered, lambda a: a.mentioned and not a.cited)
    cited_any = any(a.cited for a in answered)
    if uncited and brand_domain:
        recs.append(Recommendation(
            pillar="evidence",
            track="scripting",
            priority="P0" if not cited_any else "P1",
            title="Make owned pages citable with structured data",
            finding=(
                f"{brand} is mentioned in answers for {len(uncited)} term(s) but "
                f"{brand_domain} is not among the cited sources — engines are "
                "describing the brand from third-party material you don't control."
            ),
            action=(
                "Deploy Organization JSON-LD sitewide and page-level schema on the "
                "pages that should be the canonical source for each term, so "
                "engines can ground claims directly on your domain."
            ),
            affected_terms=uncited,
            snippet=organization_snippet(brand, brand_domain),
        ))
        recs.append(Recommendation(
            pillar="evidence",
            track="content",
            priority="P1",
            title="Create citation-magnet reference pages",
            finding=(
                "Engines cite pages that state verifiable facts plainly: stats, "
                "spec tables, definitions, original data."
            ),
            action=(
                "For each mentioned-but-uncited term, build a reference-grade page "
                "(data, methodology, dated updates) engineered to be the easiest "
                "source to quote. Refresh dates visibly — freshness drives citation."
            ),
            affected_terms=uncited,
        ))

    # --- 3. Share of voice: competitors dominate answers where you appear ---
    if competitors:
        outvoiced = _terms_by(
            answered,
            lambda a: a.mentioned and a.share_of_voice < 0.5
            and sum(a.competitor_mentions.values()) > 0,
        )
        if outvoiced:
            recs.append(Recommendation(
                pillar="authority",
                track="content",
                priority="P1",
                title="Win the comparison narrative",
                finding=(
                    f"Competitors out-mention {brand} in answers for "
                    f"{len(outvoiced)} term(s) — engines position the brand as an "
                    "also-ran rather than the default recommendation."
                ),
                action=(
                    "Publish honest head-to-head comparison pages ('{brand} vs X') "
                    "and pursue inclusion in the third-party listicles and review "
                    "roundups engines cite for these terms; those pages define the "
                    "ranking engines repeat."
                ),
                affected_terms=outvoiced,
            ))
        comp_cited = _terms_by(answered, lambda a: bool(a.competitor_cited) and not a.cited)
        if comp_cited:
            recs.append(Recommendation(
                pillar="authority",
                track="technical",
                priority="P1",
                title="Competitor domains are cited where yours is not",
                finding=(
                    "On some terms engines ground answers on competitor domains "
                    "directly — their pages are structurally easier to cite."
                ),
                action=(
                    "Audit the cited competitor pages for structure (H2 questions, "
                    "tables, schema, anchor-linkable sections) and bring your "
                    "equivalent pages to parity or better."
                ),
                affected_terms=comp_cited,
            ))

    # --- 4. Sentiment: negative or mixed framing where the brand appears ---
    negative = _terms_by(
        answered, lambda a: a.sentiment_label in ("negative", "mixed") and a.mentioned
    )
    if negative:
        recs.append(Recommendation(
            pillar="reputation",
            track="content",
            priority="P0",
            title="Neutralize negative framing at its sources",
            finding=(
                f"AI answers frame {brand} negatively or ambivalently on "
                f"{len(negative)} term(s). Engines synthesize tone from reviews, "
                "forums, and articles — the framing will persist until the "
                "underlying sources change."
            ),
            action=(
                "Trace the cited sources for these terms; address legitimate "
                "criticisms with public fixes and updated documentation, publish "
                "direct objection-handling content (pricing explainers, "
                "reliability data), and cultivate fresh positive coverage and "
                "reviews to dilute stale negatives."
            ),
            affected_terms=negative,
        ))
        recs.append(Recommendation(
            pillar="reputation",
            track="scripting",
            priority="P1",
            title="Ship FAQ schema that answers the objections",
            finding=(
                "Objection queries are being answered by third parties; FAQPage "
                "markup gives engines your on-record answer to quote instead."
            ),
            action=(
                "Add FAQPage JSON-LD to the relevant pages with direct, factual "
                "answers to the criticisms surfacing in AI responses."
            ),
            affected_terms=negative,
            snippet=faq_snippet(brand, negative),
        ))

    # --- 5. Transactional terms: PDP readiness ---
    transactional = []
    for t in terms:
        tokens = set(re.split(r"\W+", t.lower()))
        if tokens & set(TRANSACTIONAL_MARKERS):
            transactional.append(t)
    if transactional:
        weak_pdp = [
            t for t in transactional
            if any(not r.cited or not r.mentioned for r in by_term.get(t, []))
        ]
        if weak_pdp:
            recs.append(Recommendation(
                pillar="evidence",
                track="pdp",
                priority="P0",
                title="Upgrade PDPs into grounding sources for buying queries",
                finding=(
                    f"{len(weak_pdp)} transactional term(s) resolve to AI answers "
                    "that don't cite your product pages — the engine is composing "
                    "buying advice without your PDP data."
                ),
                action=(
                    "Rework PDPs so every buying question is answerable on-page: "
                    "spec tables in HTML, transparent pricing, shipping/returns "
                    "text, aggregated review counts, and a Q&A block mirroring the "
                    "questions AI answers raise for these terms."
                ),
                affected_terms=weak_pdp,
            ))
            recs.append(Recommendation(
                pillar="evidence",
                track="scripting",
                priority="P1",
                title="Deploy Product schema with offers and ratings",
                finding=(
                    "Product JSON-LD (price, availability, aggregateRating) is the "
                    "machine-readable layer engines use to trust and quote PDP "
                    "facts in shopping-intent answers."
                ),
                action=(
                    "Add complete Product markup to every PDP mapped to the "
                    "transactional terms; validate with the Rich Results test and "
                    "keep offer data in sync with the page."
                ),
                affected_terms=weak_pdp,
                snippet=product_snippet(brand, brand_domain),
            ))

    # --- 6. Cross-surface gaps: strong on one engine, absent on another ---
    surfaces = sorted({a.surface for a in answered})
    if len(surfaces) > 1:
        gap_terms: list[str] = []
        for term, rows in by_term.items():
            mentioned_surfaces = {r.surface for r in rows if r.mentioned}
            if mentioned_surfaces and mentioned_surfaces != {r.surface for r in rows}:
                gap_terms.append(term)
        if gap_terms:
            recs.append(Recommendation(
                pillar="consistency",
                track="technical",
                priority="P2",
                title="Reconcile cross-surface inconsistency",
                finding=(
                    f"For {len(gap_terms)} term(s) the brand appears on some "
                    "surfaces but not others. AI Overviews lean on top-ranking "
                    "pages; Gemini and AI Mode lean on grounded retrieval — a gap "
                    "usually means one pipeline can't see or rank your content."
                ),
                action=(
                    "Where AI Overviews miss you, improve classic organic rank and "
                    "snippet-ready formatting for the query. Where Gemini/AI Mode "
                    "miss you, check Google-Extended access and strengthen entity "
                    "signals (consistent NAP, sameAs links, knowledge-panel facts)."
                ),
                affected_terms=gap_terms,
            ))

    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    recs.sort(key=lambda r: priority_order.get(r.priority, 9))
    return recs
