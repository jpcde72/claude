"""Answer-surface providers for the GEO diagnostic.

Each provider fetches the generated answer a given AI surface returns for a
search term, plus the sources it cites:

- ``gemini``       -> Google Gemini API with Google Search grounding
                      (requires GEMINI_API_KEY)
- ``ai_mode``      -> Google AI Mode via SerpAPI (requires SERPAPI_API_KEY)
- ``ai_overview``  -> Google AI Overviews via SerpAPI (requires SERPAPI_API_KEY)

When the relevant API key is missing the factory falls back to a
deterministic mock provider so the pipeline, UI, and reports stay fully
exercisable offline. Every response is tagged ``live`` or ``mock`` so
downstream reporting never presents simulated data as real.
"""
from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field

import httpx

from app.config import settings

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
SERPAPI_ENDPOINT = "https://serpapi.com/search.json"


@dataclass
class Citation:
    url: str
    title: str = ""
    source: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SurfaceResponse:
    surface: str
    term: str
    text: str = ""
    citations: list[Citation] = field(default_factory=list)
    provider_mode: str = "live"  # live | mock
    ok: bool = True
    error: str | None = None


class SurfaceProvider(ABC):
    surface: str

    @abstractmethod
    def query(self, term: str) -> SurfaceResponse: ...


class GeminiProvider(SurfaceProvider):
    """Gemini API with Google Search grounding, so answers carry citations."""

    surface = "gemini"

    def __init__(self, api_key: str, model: str, timeout: float):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def query(self, term: str) -> SurfaceResponse:
        body = {
            "contents": [{"role": "user", "parts": [{"text": term}]}],
            "tools": [{"google_search": {}}],
        }
        try:
            resp = httpx.post(
                GEMINI_ENDPOINT.format(model=self.model),
                params={"key": self.api_key},
                json=body,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
            return SurfaceResponse(
                surface=self.surface, term=term, ok=False, error=str(exc)
            )

        candidates = data.get("candidates") or []
        if not candidates:
            return SurfaceResponse(
                surface=self.surface, term=term, ok=False, error="no candidates returned"
            )
        candidate = candidates[0]
        parts = candidate.get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)

        citations = []
        for chunk in candidate.get("groundingMetadata", {}).get("groundingChunks", []):
            web = chunk.get("web") or {}
            if web.get("uri"):
                citations.append(
                    Citation(url=web["uri"], title=web.get("title", ""))
                )
        return SurfaceResponse(
            surface=self.surface, term=term, text=text, citations=citations
        )


def _flatten_text_blocks(blocks: list[dict]) -> str:
    """Flatten SerpAPI text_blocks (paragraphs, lists, nested blocks) to text."""
    lines: list[str] = []
    for block in blocks or []:
        snippet = block.get("snippet")
        if snippet:
            lines.append(snippet)
        for item in block.get("list", []) or []:
            title = item.get("title", "")
            item_snippet = item.get("snippet", "")
            lines.append(f"{title} {item_snippet}".strip())
            if item.get("list"):
                lines.append(_flatten_text_blocks(item["list"]))
        if block.get("text_blocks"):
            lines.append(_flatten_text_blocks(block["text_blocks"]))
    return "\n".join(line for line in lines if line)


def _serpapi_citations(payload: dict) -> list[Citation]:
    citations = []
    for ref in payload.get("references", []) or []:
        if ref.get("link"):
            citations.append(
                Citation(
                    url=ref["link"],
                    title=ref.get("title", ""),
                    source=ref.get("source", ""),
                )
            )
    return citations


class SerpApiProvider(SurfaceProvider):
    """Shared SerpAPI plumbing for Google AI Mode and AI Overviews."""

    def __init__(self, api_key: str, timeout: float, gl: str, hl: str):
        self.api_key = api_key
        self.timeout = timeout
        self.gl = gl
        self.hl = hl

    def _get(self, params: dict) -> dict:
        resp = httpx.get(
            SERPAPI_ENDPOINT,
            params={"api_key": self.api_key, "gl": self.gl, "hl": self.hl, **params},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()


class AIModeProvider(SerpApiProvider):
    surface = "ai_mode"

    def query(self, term: str) -> SurfaceResponse:
        try:
            data = self._get({"engine": "google_ai_mode", "q": term})
        except httpx.HTTPError as exc:
            return SurfaceResponse(
                surface=self.surface, term=term, ok=False, error=str(exc)
            )
        text = _flatten_text_blocks(data.get("text_blocks", []))
        return SurfaceResponse(
            surface=self.surface,
            term=term,
            text=text,
            citations=_serpapi_citations(data),
        )


class AIOverviewProvider(SerpApiProvider):
    surface = "ai_overview"

    def query(self, term: str) -> SurfaceResponse:
        try:
            data = self._get({"engine": "google", "q": term})
            overview = data.get("ai_overview") or {}
            # Some AI Overviews require a follow-up request with a page token.
            if overview.get("page_token") and not overview.get("text_blocks"):
                overview = self._get(
                    {"engine": "google_ai_overview", "page_token": overview["page_token"]}
                ).get("ai_overview", {})
        except httpx.HTTPError as exc:
            return SurfaceResponse(
                surface=self.surface, term=term, ok=False, error=str(exc)
            )

        if not overview or not overview.get("text_blocks"):
            # No AI Overview shown for this query is itself a diagnostic signal.
            return SurfaceResponse(
                surface=self.surface, term=term, text="", citations=[]
            )
        return SurfaceResponse(
            surface=self.surface,
            term=term,
            text=_flatten_text_blocks(overview.get("text_blocks", [])),
            citations=_serpapi_citations(overview),
        )


class MockProvider(SurfaceProvider):
    """Deterministic simulated surface for offline runs and tests.

    Output varies by (surface, term) hash so a multi-term audit produces a
    realistic mix of presence, citation, and sentiment outcomes.
    """

    def __init__(self, surface: str, brand: str, brand_domain: str, competitors: list[str]):
        self.surface = surface
        self.brand = brand
        self.brand_domain = brand_domain or f"{brand.lower().replace(' ', '')}.com"
        self.competitors = competitors or ["Rivalio", "Competex"]

    def query(self, term: str) -> SurfaceResponse:
        digest = hashlib.sha256(f"{self.surface}:{term}".encode()).hexdigest()
        bucket = int(digest, 16) % 10
        rival = self.competitors[int(digest[:8], 16) % len(self.competitors)]

        citations = [
            Citation(url=f"https://en.wikipedia.org/wiki/{term.replace(' ', '_')}",
                     title=term.title(), source="Wikipedia"),
            Citation(url=f"https://{rival.lower().replace(' ', '')}.com/guide",
                     title=f"{rival} guide", source=rival),
        ]

        if bucket <= 4:  # strong presence: mentioned, cited, positive
            text = (
                f"When it comes to {term}, {self.brand} is widely regarded as a reliable "
                f"and trusted option, praised for excellent quality and helpful support. "
                f"Alternatives such as {rival} are also popular. Reviewers consistently "
                f"recommend {self.brand} for most buyers."
            )
            citations.insert(
                0,
                Citation(url=f"https://{self.brand_domain}/resources/{term.replace(' ', '-')}",
                         title=f"{self.brand} on {term}", source=self.brand),
            )
        elif bucket <= 6:  # mentioned but not cited, neutral
            text = (
                f"There are several options for {term}. {self.brand} offers a standard "
                f"product in this category, while {rival} focuses on the premium segment. "
                f"The best choice depends on budget and requirements."
            )
        elif bucket == 7:  # mentioned with negative framing
            text = (
                f"For {term}, some users report that {self.brand} can be unreliable and "
                f"expensive compared to alternatives, with complaints about slow support. "
                f"{rival} is often suggested as a better, more trusted alternative."
            )
        else:  # absent: competitor-only answer
            text = (
                f"The leading choices for {term} include {rival} and a few niche providers. "
                f"{rival} stands out for its outstanding reputation and excellent value."
            )

        return SurfaceResponse(
            surface=self.surface,
            term=term,
            text=text,
            citations=citations,
            provider_mode="mock",
        )


def get_provider(
    surface: str,
    brand: str = "",
    brand_domain: str = "",
    competitors: list[str] | None = None,
) -> SurfaceProvider:
    """Return a live provider when credentials exist, else the mock."""
    if surface == "gemini" and settings.GEMINI_API_KEY:
        return GeminiProvider(
            settings.GEMINI_API_KEY, settings.GEMINI_MODEL, settings.GEO_HTTP_TIMEOUT
        )
    if surface == "ai_mode" and settings.SERPAPI_API_KEY:
        return AIModeProvider(
            settings.SERPAPI_API_KEY, settings.GEO_HTTP_TIMEOUT,
            settings.GEO_GL, settings.GEO_HL,
        )
    if surface == "ai_overview" and settings.SERPAPI_API_KEY:
        return AIOverviewProvider(
            settings.SERPAPI_API_KEY, settings.GEO_HTTP_TIMEOUT,
            settings.GEO_GL, settings.GEO_HL,
        )
    return MockProvider(surface, brand, brand_domain, competitors or [])
