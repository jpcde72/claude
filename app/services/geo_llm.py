"""Live Q&A against Claude, grounded in the GEO/AXO knowledge model and the brand project."""

import logging
import os
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

import anthropic

from app.config import settings
from app.models_geo import Asset, BrandProject, LLMExchange
from app.services.geo_knowledge import ari_score, knowledge_digest, load_doc

log = logging.getLogger(__name__)
NO_CREDENTIALS = "No Anthropic credentials found. Set ANTHROPIC_API_KEY and restart GEO Studio."

ROLE = """You are the strategist inside GEO Studio, a workspace for generative engine optimisation (GEO) \
and agentic experience optimisation (AXO). You advise brand, media and ecommerce leaders on how to be \
found, chosen, bought and re-bought when the buyer is an AI answer engine or an agent acting for a person \
(Meta Muse, ChatGPT, Gemini and AI Mode, Siri AI, Alexa for Shopping, Copilot, B2B buying agents).

Ground every answer in the knowledge model below: tag recommendations with layer (Entity, Surface, \
Protocol, Mandate), arena (Eligibility, Justification, Defaults) and Delegation rung (D0-D4) where useful, \
and cite workstream, prediction and action IDs (W15, P3, A2). Date landscape claims. Separate paid from \
earned. State uncertainty plainly; never promise placement in any AI answer. When the brand context is \
thin, say what data would change the recommendation. Write in clear, structured markdown: short headings, \
tables where they compare, and a closing "Next moves" list with owner and KPI when giving advice. \
If web search is available, use it for anything that may have changed since the model's as-of date and \
say what is new."""


@dataclass
class AskRequest:
    question: str
    project: BrandProject | None = None
    assets: list[Asset] = field(default_factory=list)
    history: list[LLMExchange] = field(default_factory=list)
    web_search: bool = False


def system_blocks(req: AskRequest) -> list[dict]:
    # Stable prefix first so it caches across every question; project context varies after it.
    stable = (
        f"{ROLE}\n\n<knowledge_model>\n{knowledge_digest()}\n</knowledge_model>\n\n"
        f"<outlook_2027>\n{load_doc('outlook')}\n</outlook_2027>\n\n"
        f"<playbook>\n{load_doc('playbook')}\n</playbook>"
    )
    blocks = [{"type": "text", "text": stable, "cache_control": {"type": "ephemeral"}}]
    context = project_context(req)
    if context:
        blocks.append({"type": "text", "text": context})
    return blocks


def project_context(req: AskRequest) -> str:
    p = req.project
    if p is None:
        return ""
    lines = [
        "<brand_project>",
        f"Name: {p.name}",
        f"Sector: {p.sector or 'unknown'} | Market: {p.market or 'unknown'} | Segment: {p.segment}",
        f"Website: {p.website or 'unknown'}",
        f"Competitors: {p.competitors or 'not set'}",
        f"Notes: {p.notes or 'none'}",
    ]
    if p.ari:
        lines.append(f"ARI v2 component scores: {p.ari} -> index {ari_score(p.ari)}")
    lines.append("</brand_project>")
    for a in req.assets:
        if a.current:
            lines.append(
                f'<asset id="{a.id}" kind="{a.kind}" title="{a.title}" version="{a.current.version}">\n'
                f"{a.current.content}\n</asset>"
            )
    return "\n".join(lines)


def build_messages(req: AskRequest) -> list[dict]:
    messages: list[dict] = []
    for ex in req.history:
        if ex.answer:
            messages.append({"role": "user", "content": ex.question})
            messages.append({"role": "assistant", "content": ex.answer})
    messages.append({"role": "user", "content": req.question})
    return messages


def _sources_footer(message) -> str:
    urls: dict[str, str] = {}
    for block in message.content:
        if block.type == "web_search_tool_result" and isinstance(block.content, list):
            for r in block.content:
                if getattr(r, "url", None):
                    urls.setdefault(r.url, r.title or r.url)
    if not urls:
        return ""
    items = "\n".join(f"- [{title}]({url})" for url, title in list(urls.items())[:12])
    return f"\n\n**Web sources**\n{items}\n"


async def stream_answer(req: AskRequest) -> AsyncIterator[dict]:
    """Yield events: {"type": "status"|"text"|"error"|"final", ...}."""
    try:
        # Keys not scoped to a workspace must name one on every request.
        workspace = os.environ.get("ANTHROPIC_WORKSPACE_ID", "").strip()
        headers = {"anthropic-workspace-id": workspace} if workspace else None
        client = anthropic.AsyncAnthropic(default_headers=headers)
    except anthropic.AnthropicError:
        yield {"type": "error", "message": NO_CREDENTIALS}
        return

    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}] if req.web_search else []
    messages = build_messages(req)
    answer = ""

    try:
        for _ in range(4):  # resume server-tool pause_turn a few times at most
            async with client.beta.messages.stream(
                model=settings.GEO_MODEL,
                max_tokens=settings.GEO_MAX_TOKENS,
                system=system_blocks(req),
                messages=messages,
                thinking={"type": "adaptive"},
                output_config={"effort": "medium"},
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                **({"tools": tools} if tools else {}),
            ) as stream:
                async for event in stream:
                    if event.type == "text":
                        answer += event.text
                        yield {"type": "text", "text": event.text}
                    elif event.type == "content_block_start" and event.content_block.type == "server_tool_use":
                        yield {"type": "status", "message": "Searching the web…"}
                final = await stream.get_final_message()

            if final.stop_reason == "refusal":
                yield {"type": "error", "message": "Claude declined this request. Try rephrasing it."}
                return
            footer = _sources_footer(final)
            if footer:
                answer += footer
                yield {"type": "text", "text": footer}
            if final.stop_reason != "pause_turn":
                break
            messages.append({"role": "assistant", "content": final.content})
    except anthropic.AuthenticationError:
        yield {"type": "error", "message": "The Anthropic API key was rejected. Check ANTHROPIC_API_KEY."}
        return
    except anthropic.RateLimitError:
        yield {"type": "error", "message": "Rate limited by the Anthropic API. Try again shortly."}
        return
    except anthropic.APIStatusError as e:
        yield {"type": "error", "message": f"Anthropic API error {e.status_code}: {e.message}"}
        return
    except anthropic.APIConnectionError:
        yield {"type": "error", "message": "Could not reach the Anthropic API."}
        return
    except anthropic.AnthropicError as e:
        yield {"type": "error", "message": f"Claude is unavailable: {e}"}
        return
    except TypeError as e:
        # The SDK raises TypeError at request time when no credential source resolves.
        if "authentication" not in str(e):
            log.exception("GEO Studio ask failed")
            yield {"type": "error", "message": "Something went wrong while asking Claude."}
            return
        yield {"type": "error", "message": NO_CREDENTIALS}
        return

    yield {"type": "final", "answer": answer, "model": settings.GEO_MODEL}
