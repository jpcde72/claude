# The Growth Grid — a unified growth system

*v0.1 (draft). Combines **Intent Planning** (the consumer-intent-modeler and intent-planner skills), **First-Principles Media** and the **Media Operating System**. Status: an architecture to test. It has not been validated.*

---

## 1. The thesis

> **Target no one. Serve every moment. Be the default for machines.**

The three parent frameworks look like they disagree:

| Framework | Its core claim | Its blind spot |
|---|---|---|
| First-Principles Media | Segments are mostly fiction. Growth comes from broad reach to light buyers. | Says little about *when* and *why* people buy, or what to build beyond ads |
| Intent Planning | People buy in need states. Personal data enables branded utility. | Read naively, it pulls toward personalised targeting, which breaks Truths 2 and 3 |
| Media OS | Reach, then social transmission, then protocol (agents) | Has no intent or occasion axis. Layers are planned per market, not per moment |

**The reconciliation, and what makes this system distinct:** a need state is not an audience. It is a **category entry point (CEP) cluster**, a *moment* that every category buyer passes through. Once intent is read as *moments* rather than *people*, the three frameworks slot together:

- **First-Principles** answers *who* (everyone who buys the category) and *how much* (reach-curve maths).
- **Intent** answers *when and why*: which moments to build memory against, and which moments deserve a utility.
- **Media OS** answers *how it spreads* (transmission) and *who decides* (humans or agents).

Most of the market still runs "brand vs performance" as two opposed systems. The Growth Grid replaces that split with one unit of planning, the **Moment**.

---

## 2. The grid

**Rows = the six Moments** (the intent-planner's need states). **Columns = the three Media OS layers plus a Utility layer.**

| Moment | L1 Reach (memory) | L2 Transmission (social) | L3 Protocol (machines) | U — Utility (permissioned data) |
|---|---|---|---|---|
| **Replenish** — "running low" | Distinctive assets linked to the routine CEP | Low; habits don't travel much | **Highest.** First moment handed to agents: defaults, subscriptions, structured product data | Auto-replenish, reorder memory |
| **Plan** — "this week" | CEPs for planning occasions | Household / Nested Dunbar | High: agents assemble plans and baskets | Planners, list builders |
| **Discover** — "something new" | Broad reach of *new* news | **Highest**: Viral Mesh and Identity Tribe | Medium: AI search, curated answers | Recommendation and inspiration tools |
| **Manage** — "needs handling" | CEPs for problem and constraint | Authority and gatekeeper groups (experts, clinicians) | Medium-high: justification arena, verifiable claims | Diagnostic or constraint tools (Tier 2–3 data) |
| **Celebrate** — "this matters" | Occasion bursts, common knowledge | **High**: normative and public | Low: stays human | Shareable, "Wrapped"-style content |
| **Care** — "my responsibility" | Long-run brand codes | Multiplex, strong-tie communities | **Lowest**: identity decisions resist delegation | Ongoing-care utilities, high trust bar |

Column rules, taken from the parents and not negotiable:

1. **L1 covers every row and is funded first**, up to the reach-curve efficient frontier (Truths 1–3). A Moment changes the *creative's CEP link*, never the *size of the audience*.
2. **L2 changes form and vernacular, never reach** (Media OS heuristic 1 and heuristic 7).
3. **L3 is weighted by the Delegation Gradient** (§3).
4. **U personalises on request (pull), never through push targeting.** Personal data improves the service a person opts into. It never shrinks who the ads reach. This is how the intent-planner's personal-data thesis fits with Truth 2.

---

## 3. The new mechanism: the Delegation Gradient

*Inferred hypothesis, not yet measured.*

Moments differ in how willingly people hand them to AI agents. Low-cognition, routine moments (Replenish, Plan) get delegated first. Identity-laden moments (Care, Celebrate) get delegated last. So the **human-memory vs machine-eligibility investment split should differ by Moment, not by channel**.

**How to operationalise it:** use the consumer-intent-modeler's **AGNT domain** scores (Delegation Confidence, Effort Minimisation, Transparency, Override Availability). Push them through the intent→need-state crosswalk to get a **Delegation Index (0–1) per Moment**.

```
Moment weight in L3 (Protocol) ∝ Heat(moment) × DelegationIndex(moment)
Moment weight in L1 creative   ∝ Heat(moment) × (1 − DelegationIndex(moment)) + floor
```

L1 *budget* is never cut by this. The gradient only reallocates **creative and CEP emphasis** within L1, and **build effort** in L3. The `floor` keeps memory-building going in every Moment. Humans still set the agent's rules, and 24% of consumers say they will never delegate purchases ([Checkout.com, 2026](https://www.checkout.com/newsroom/consumer-demand-for-ai-shopping-is-forming-fast-but-trust-for-agentic-commerce-is-still-catching-up)).

---

## 4. Why now (the media landscape, 2026–2028)

| Signal | Status | Implication for the grid |
|---|---|---|
| AI answers absorb search clicks. Users clicked on 8% of searches that showed an AI Overview vs 15% without one (Pew); overall zero-click rate ~68% (Similarweb/SparkToro, Jun 2026) | **Known** (secondary sources) | The Discover and Manage rows lose click-based harvesting. L3 eligibility and justification become where the demand gets captured |
| Agent checkout protocols have launched: ACP (OpenAI + Stripe, Sep 2025), UCP (Google + Shopify, Jan 2026), AP2, and MCP under the Linux Foundation | **Known** | The Replenish and Plan rows can be transacted by agents. Structured data and defaults become the "creative" there |
| Demand for AI shopping is rising faster than trust in it, and merchant infrastructure is immature | **Known** (vendor surveys, so treat with care) | The Delegation Gradient is real but moves slowly. Don't over-rotate L1 money into L3 |
| Retail media and CTV keep growing as reach channels | **Inferred** (not re-verified this session) | Better reach supply for L1. Retail media is not a targeting licence |

---

## 5. The operating loop

1. **Map the Moments.** Run consumer-intent-modeler (47 intents) → evidence analyzer → crosswalk → **Heat per Moment**.
2. **Measure delegation.** Take the AGNT domain → **Delegation Index per Moment**.
3. **Fund L1.** Broad reach to the efficient frontier. Build one distinctive-asset system, with CEP-linked creative weighted by Heat.
4. **Read the market signature (L2).** Find the 2–3 dominant archetypes and which Moment each one hosts.
5. **Build L3 per Moment.** Work the Eligibility → Justification → Defaults arenas, ordered by Heat × Delegation.
6. **Pick utilities (U).** Use intent-planner ideas ranked by Impact × Feasibility × Data-friction, restricted to the top-Heat Moments.
7. **Measure by layer.** L1: mental availability *per CEP/Moment* plus reach delivery. L2: transmission proxies. L3: Recommendation Equity Index per Moment. Causal proof comes from incrementality tests, not attribution.
8. **Compound.** Tag every flight by Moment × creative pillar, so the Benchmark Bank (signal-moat-architect) grows *by Moment*. That turns the system into a moat.

---

## 6. Guard rails (the weakest-hypothesis check on the system itself)

- **The grid is a diagnostic, not a plan.** Activate only cells with real Heat. A brand might run 6 L1 rows, 2 L3 rows and 1 utility. Filling all 24 cells is over-specification.
- **If an output narrows who the ads reach, it has failed.** Moments decide the message and the build, never the audience.
- **The Delegation Index is a hypothesis.** Validate it against observed agent-referred share per Moment before it moves real money.
- **IP boundary.** This combines frameworks built partly in an employer context. Settle ownership (employer vs personal) before productising, as signal-moat-architect already flags.

---

## 7. Open questions to build next

1. Where do AGNT intents map in the crosswalk? This decides whether the Delegation Index can be computed from existing outputs.
2. Which pilot brand × market has enough intent data *and* measurable agent-referred traffic?
3. Should the Growth Grid become a skill that orchestrates the parents (`growth-grid`), in the same way Media OS orchestrates its two parents?
