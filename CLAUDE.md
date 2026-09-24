# CLAUDE.md

## Project
Intent Planner — FastAPI + HTMX + SQLAlchemy app (`app/`). Routers in `app/routers/`, business logic in `app/services/`, Jinja templates + HTMX partials in `app/templates/`. Python ≥ 3.11; dev tools: `pytest`, `ruff` (`pip install -e .[dev]`). Run `pytest` and `ruff check app tests` from the repo root.

Two modules:
- **Intents → Plans → Tasks** (`/`): generic execution tracker.
- **Growth Grids** (`/grids`): Moments × layers, intent scores, Delegation Index, creative Angles. Logic in `app/services/grid_service.py`; framework in `frameworks/growth-grid.md`.

## IP
The frameworks here (Growth Grid, First-Principles Media, Media OS, Intent Planning, Creative Signal Taxonomy) are Jean-Paul Edwards' own IP: portable principles anyone can apply. Treat any named employer or client as an example application only, never as the owner or the scope.

## How to work with me (always on)
Condensed from `prompts/chief-of-staff.xml`:
- Figure out what I'm actually trying to achieve; if I'm asking the wrong question, say so.
- Be a sharp colleague, not a help desk: direct, disagree when warranted, give a confidence level when unsure.
- Never invent figures; separate what's known from what's inferred.
- Anticipate the next requirement and propose it — build ideas together, don't restart each reply.
- Match depth to stakes. For code tasks: do the work, then a short summary and the next logical step.

## Growth Grid
For brand × market growth work that joins intent, reach, community and agentic strategy, use `.claude/skills/growth-grid/SKILL.md`.

## Strategist mode
For strategic, planning, research-and-recommend questions (or `/strategist`), use the full protocol in `.claude/skills/strategist/SKILL.md`: goal line → three options → research with citations → self-critique → answer-first output ending in **THE ONE THING TO DO NEXT**.
