"""Diagnostic analysis of AI-surface answers.

Given a surface response and the audited brand, this module measures:

- presence:   is the brand mentioned at all, how often, and how early
- citation:   is the brand's own domain among the cited sources
- sentiment:  how the answer frames the brand where it is mentioned
- share of voice: brand mentions vs. competitor mentions
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

from app.services.geo.providers import SurfaceResponse

POSITIVE_WORDS = {
    "best", "excellent", "great", "reliable", "trusted", "recommend",
    "recommended", "leading", "outstanding", "praised", "top", "popular",
    "quality", "helpful", "favorite", "favourite", "innovative", "loved",
    "strong", "well-regarded", "regarded", "value", "affordable", "premium",
}
NEGATIVE_WORDS = {
    "worst", "poor", "unreliable", "avoid", "complaints", "complaint",
    "expensive", "slow", "bad", "issues", "problem", "problems", "scam",
    "negative", "disappointing", "lawsuit", "recall", "criticized",
    "criticised", "downside", "downsides", "weak", "untrusted", "risky",
}

SENTIMENT_WINDOW = 180  # chars of context inspected around each brand mention


@dataclass
class TermAnalysis:
    term: str
    surface: str
    provider_mode: str = "live"
    answered: bool = True          # surface produced an answer at all
    mentioned: bool = False
    mention_count: int = 0
    prominence: float = 0.0        # 1.0 = brand appears at the very start
    cited: bool = False
    citation_domains: list[str] = field(default_factory=list)
    citations: list[dict] = field(default_factory=list)
    competitor_mentions: dict[str, int] = field(default_factory=dict)
    competitor_cited: list[str] = field(default_factory=list)
    sentiment_score: float = 0.0   # -1.0 .. 1.0
    sentiment_label: str = "not_mentioned"
    evidence: str = ""             # first mention context, quoted in reports
    error: str | None = None

    @property
    def share_of_voice(self) -> float:
        rival_total = sum(self.competitor_mentions.values())
        total = self.mention_count + rival_total
        if total == 0:
            return 0.0
        return self.mention_count / total


def brand_variants(brand: str) -> list[str]:
    """Name variants matched as brand mentions (e.g. 'Acme Corp' / 'AcmeCorp')."""
    brand = brand.strip()
    variants = {brand}
    if " " in brand:
        variants.add(brand.replace(" ", ""))
        variants.add(brand.replace(" ", "-"))
    return [v for v in variants if v]


def _mention_pattern(names: list[str]) -> re.Pattern:
    alternation = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
    return re.compile(rf"(?<![\w-])({alternation})(?![\w-])", re.IGNORECASE)


def extract_domain(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def _sentiment_around(text: str, positions: list[int]) -> float:
    """Lexicon score over context windows around each mention position."""
    pos_hits = 0
    neg_hits = 0
    for idx in positions:
        window = text[max(0, idx - SENTIMENT_WINDOW): idx + SENTIMENT_WINDOW].lower()
        tokens = set(re.findall(r"[a-z][a-z-]+", window))
        pos_hits += len(tokens & POSITIVE_WORDS)
        neg_hits += len(tokens & NEGATIVE_WORDS)
    total = pos_hits + neg_hits
    if total == 0:
        return 0.0
    return (pos_hits - neg_hits) / total


def _label(score: float, mentioned: bool) -> str:
    if not mentioned:
        return "not_mentioned"
    if score >= 0.25:
        return "positive"
    if score <= -0.25:
        return "negative"
    if score != 0.0:
        return "mixed"
    return "neutral"


def analyze_response(
    response: SurfaceResponse,
    brand: str,
    brand_domain: str = "",
    competitors: list[str] | None = None,
) -> TermAnalysis:
    analysis = TermAnalysis(
        term=response.term,
        surface=response.surface,
        provider_mode=response.provider_mode,
        error=response.error,
    )
    if not response.ok:
        analysis.answered = False
        return analysis

    text = response.text or ""
    analysis.answered = bool(text.strip())
    analysis.citations = [c.to_dict() for c in response.citations]
    analysis.citation_domains = sorted(
        {extract_domain(c.url) for c in response.citations if c.url}
    )

    if not analysis.answered:
        return analysis

    pattern = _mention_pattern(brand_variants(brand))
    matches = list(pattern.finditer(text))
    analysis.mentioned = bool(matches)
    analysis.mention_count = len(matches)

    if matches:
        first = matches[0].start()
        analysis.prominence = round(1.0 - (first / max(len(text), 1)), 3)
        start = max(0, first - 80)
        end = min(len(text), first + 200)
        analysis.evidence = text[start:end].strip()
        analysis.sentiment_score = round(
            _sentiment_around(text, [m.start() for m in matches]), 3
        )
    analysis.sentiment_label = _label(analysis.sentiment_score, analysis.mentioned)

    if brand_domain:
        target = extract_domain(f"https://{brand_domain}") or brand_domain.lower()
        analysis.cited = any(
            d == target or d.endswith(f".{target}") for d in analysis.citation_domains
        )

    for competitor in competitors or []:
        comp_pattern = _mention_pattern(brand_variants(competitor))
        count = len(comp_pattern.findall(text))
        if count:
            analysis.competitor_mentions[competitor] = count
        comp_domain = competitor.lower().replace(" ", "")
        if any(comp_domain in d for d in analysis.citation_domains):
            analysis.competitor_cited.append(competitor)

    return analysis
