# Intent Planner + GEO Studio

Two FastAPI apps share one server:

| Path | App |
|---|---|
| `/` | **Intent Planner**: intents → plans → tasks with dependencies |
| `/geo` | **GEO Studio**: navigate GEO/AXO strategy, ask Claude live questions, store versioned assets per brand project |

## Run

```bash
pip install -e ".[dev]"
export ANTHROPIC_API_KEY=...          # needed only for live questions
uvicorn app.main:app --reload
# open http://localhost:8000/geo
```

Optional settings (environment variables):

| Variable | Default | Purpose |
|---|---|---|
| `INTENT_PLANNER_DATABASE_URL` | `sqlite:///./intent_planner.db` | Storage for both apps |
| `INTENT_PLANNER_GEO_MODEL` | `claude-opus-5` | Claude model used by GEO Studio |
| `INTENT_PLANNER_GEO_MAX_TOKENS` | `32000` | Answer length cap |

Tests: `pytest -q`.

## GEO Studio

- **Knowledge**: layers × arenas × the Delegation Ladder, ten new-thinking concepts, workstreams W1–W20, agent surfaces (Meta Muse, ChatGPT, Google AI Mode/Gemini, Siri AI, Alexa for Shopping, Copilot, Agentforce, Perplexity), protocols (UCP, ACP, AP2, TAP, Agent Pay, MCP, A2A, App Intents, NLWeb, llms.txt), ARI v2, predictions P1–P12, actions A1–A12 and sources. Filter by text or layer; every card has an **Ask** button.
- **2027 outlook** and **Playbook**: the long-form research, rendered.
- **Brand projects**: a brief, an ARI v2 scorer with a live index, and starter kits that generate a readiness brief, 2027 plan, probe set, Muse memo, mandate strategy or access audit.
- **Assets**: markdown documents with full version history. Edit, restore any version, export a project as `.md`, or **Refresh with Claude** to save an updated version.
- **Ask Claude drawer** (every page): streams answers grounded in the knowledge model, the project brief and any assets you tick. It has an optional **web search** toggle, keeps follow-up context within a thread, and **saves** any answer as a new asset or as the next version of an existing one. Server-side refusal fallbacks are enabled (`fallbacks: "default"`).
- **Visual systems**: a **JP | OM** toggle in the header switches between the JP Meridian (Tropical) system and the Omnicom Media system. The choice is remembered per browser.

## Skills

`skills/` holds the versioned skill sources:

- `skills/geo-axo-strategist/`: **new**. Brand-level GEO/AXO: the Mandate layer, the Delegation Ladder, W15–W20, ARI v2, surfaces and protocols, predictions and actions. `assets/knowledge.json` is the canonical model, and GEO Studio reads the same file, so edit it there.
- `skills/local-discovery-os/`: **updated to v2**. Adds readiness rung 6 (verified-agent payment), the Cloudflare default-blocking note, W15–W19 applied to local businesses, and an ARI v2 migration note.

To update your installed skills, upload these folders through your skills settings. The synced copies are read-only in this environment.
