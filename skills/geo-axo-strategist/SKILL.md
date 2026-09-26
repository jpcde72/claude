---
name: geo-axo-strategist
description: Brand-level GEO (generative engine optimisation) and AXO (agentic experience optimisation) strategy for national, ecommerce and B2B brands. Covers being cited by AI answers and being chosen, bought and re-bought by personal and business agents such as Meta Muse, ChatGPT, Gemini and AI Mode, Siri AI, Alexa for Shopping, Copilot and Agentforce. Use whenever the user asks about AI search visibility for a brand, agent readiness, agentic commerce (UCP, ACP, AP2, MCP), Meta Muse or other personal agents, what brands should do for 2027, share of answer, the Agent Readiness Index, brand agents, or B2B buying agents. Trigger on "GEO", "AXO", "agentic commerce", "Muse", "agent readiness", "share of answer", "will agents recommend us", "AI shopping agents", "prepare for 2027". For single-location or local service businesses, use local-discovery-os instead (this skill shares its ontology).
---

# GEO / AXO Strategist

Makes a brand **findable, choosable, transactable and retained** when the buyer is a model or an agent acting for a person.

This skill extends `local-discovery-os` (LDOS) from local businesses to brands. It keeps LDOS's ontology, evidence rules and workstreams W1–W14, and adds:

- a fourth layer, **Mandate**, for what happens after a person delegates the decision;
- the **Delegation Ladder** (D0 Ask to D4 Autopilot);
- six agentic workstreams, **W15–W20**;
- **Agent Readiness Index v2** (seven components);
- a dated **surface and protocol register**, **predictions to end-2027** and a **ranked action set**.

The canonical model is `assets/knowledge.json`. GEO Studio (the app in this repo) reads the same file. **Edit the JSON, not copies of it.** Bump `meta.version` and `meta.as_of` on every change.

---

## 1. The reframe for 2026–27

The LDOS reframe still holds: ranked lists rendered to humans are collapsing into 1–3 option answers. Three things changed in 2026 and they move the centre of gravity from D0–D1 to D3–D4:

1. **Personal agents shipped at consumer scale.** Meta Muse (8 Sep 2026) browses the open web in its own VM, remembers the user and buys through Link by Stripe. Siri AI (Sep 2026) acts across apps through App Intents using personal context. Alexa for Shopping (May 2026) buys from other retailers and auto-buys at a target price.
2. **The commerce rails exist.** Google UCP (Jan 2026), OpenAI/Stripe ACP, Google AP2 mandates, Visa Trusted Agent Protocol and Mastercard Agent Pay. Most brands can turn these on through their PSP or platform, with no replatforming.
3. **Paid units moved inside agents.** ChatGPT feed ads (Jun 2026) and Sponsored Agents (Sep 2026), ads in AI Mode, sponsored answers in Alexa. Muse has no ads yet, and they are the obvious next step.

Consequence: **persuasion work depreciates, while evidence, protocol and mandate work appreciate.** An agent that cannot resolve your product, verify your claim, pass your bot wall or complete checkout never reaches your creative.

## 2. Layers × arenas × rungs

Tag every gap, recommendation and task with **layer** (Entity, Surface, Protocol, Mandate), **arena** (Eligibility, Justification, Defaults) and the **Delegation rung** it serves. If a task serves none, cut it.

| Rung | Name | What wins |
|---|---|---|
| D0 | Ask | Retrieved and cited |
| D1 | Advise | Shortlisted, with a justification the model can repeat |
| D2 | Arrange | Legible offer, price and stock; clean hand-off |
| D3 | Act | Protocol support, verified-agent acceptance, reliability record |
| D4 | Autopilot | Stored default; service record that survives re-audit |

## 3. Which reference to load

| You are doing | Read |
|---|---|
| Any strategy, audit or recommendation | `references/playbook.md` |
| Landscape questions ("what is Muse", "which protocol") | `assets/knowledge.json` → `surfaces`, `protocols` |
| Forecasts, 2027 planning, board narratives | `references/predictions-2027.md` |
| Entity, surface, probing and schema work (W1–W14) | `local-discovery-os/references/workstreams.md` and `geo-axo.md` |
| Scoring | `assets/knowledge.json` → `ari`; method in `references/playbook.md` §4 |

## 4. Pipeline (brand version)

1. **Scope.** Brand, markets, categories, segments (consumer, B2B or both), competitor set, surfaces that matter by market.
2. **Canonicalise.** Product and offer graph: names, GTINs, variants, claims with evidence, policies. This is LDOS W1–W4 at SKU level.
3. **Access audit (W15).** Do this first. It takes 30 minutes and can invalidate everything else.
4. **Observe.** Probe set per surface (W14 + W17), agent journey test per surface (W16), feed QA, evidence census.
5. **Score.** ARI v2 with components. Record confidence per component.
6. **Prescribe.** One ranked backlog, using the action template in `playbook.md`. Default ordering comes from `knowledge.json` → `actions`.
7. **Build and measure.** Change-event log, probe time series, agent traffic segment.
8. **Re-forecast quarterly.** Check `predictions` against their `signals`, re-grade confidence, and update the JSON.

## 5. Standing rules (in addition to LDOS rules)

1. **Surfaces are never pooled.** Report share of answer per surface; Muse and Alexa are different markets with different walls.
2. **Label paid versus earned.** A sponsored agent placement is not a recommendation. Keep them in separate columns.
3. **Date every landscape claim.** This field changes monthly. Every surface or protocol statement carries an as-of date and a source.
4. **No guaranteed placement.** There is still no submission API for recommendations. The LDOS "what we do not claim" list applies unchanged.
5. **Predictions carry confidence and signals.** A prediction without a falsifying signal is an opinion, so label it as one.
6. **Data foundations before bespoke agents.** A brand agent grounded in a broken catalogue produces confident errors at scale.

## 6. Output shapes

- **Readiness brief** (1 page): ARI v2 with components, top 3 cheapest moves, per-surface probe snapshot.
- **2027 plan**: ranked actions A1–A12 tailored to the brand, with owner, KPI and quarter.
- **Surface memo**: one surface in depth (for example "What Muse means for Brand X").
- **Probe pack**: fixed prompts by intent class × surface, run protocol, extraction fields.

For client-facing output, route to `om-pptx-pro` (OM deck) or `tropical-asset-studio` / `visual-explainer` (JP brand). For a live workspace, point the user to **GEO Studio** in this repo (`/geo`).
