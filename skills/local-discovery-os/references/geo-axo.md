# Protocol Layer: GEO and AXO

**GEO** (generative engine optimisation) — being *retrieved, understood, and cited* when a generative system answers a question.
**AXO** (agentic experience optimisation) — being *eligible, justifiable, and transactable* when a software agent acts on a user's behalf.

The distinction matters. GEO is about being in the answer. AXO is about surviving contact with an agent that then has to *do something*. A business can win GEO and lose AXO entirely: recommended, then dropped at the booking step because the agent couldn't get a quote or a slot.

---

## 1. Why the classical model breaks

Classical local SEO optimises for a ranked list rendered to a human who then chooses. Three things break that model:

1. **Answer collapse.** Ten results become one to three. Positions 4–10, which currently carry real traffic, stop existing as a destination.
2. **Intermediated choice.** The chooser is a model applying an implicit policy, not a person scanning. Persuasion moves from layout and copy to evidence and corroboration.
3. **Delegated action.** When the agent books, the criteria shift from "most appealing listing" to "most reliably completable transaction". Availability, price legibility, and API-level responsiveness become ranking factors in everything but name.

The strategic consequence: **work at the Entity and Protocol layers appreciates; work purely at the Surface layer depreciates.** Prioritise accordingly, and say so to the client — it is the most defensible thing in the whole proposition.

---

## 2. The three arenas, applied

| Arena | Human search | Generative answer | Agentic action |
|---|---|---|---|
| **Eligibility** | Category, service area, hours | Entity resolvable; claims retrievable and corroborated | Meets hard filters: verified coverage, licensing, capacity, price band, machine-checkable availability |
| **Justification** | Reviews, rating, photos, copy | Evidence density; third-party corroboration; specificity; recency | Reliability record, response latency, quote accuracy, completion rate |
| **Defaults** | Pack position, proximity | Position in shortlist; whether cited or merely summarised | Whether the agent can complete end-to-end without human fallback |

**Design rule:** never optimise a justification signal while an eligibility gate is failing. An agent that cannot confirm you serve the postcode never evaluates your reviews.

---

## 3. W12 — Structured data and entity graph

**Purpose** Make the entity machine-resolvable and its claims machine-checkable.

**Tasks**
1. **T12.1 Schema inventory.** Crawl every page; record types present, required properties present, validity errors, and whether markup matches visible content (mismatch is a penalty risk and a trust failure).
2. **T12.2 Core coverage.** Minimum viable set for a local service business:
   - `LocalBusiness` (or the correct specific subtype) on the home and location pages
   - `Service` on every service and service×city page, with `areaServed`, `provider`, `serviceType`, `offers` with `priceSpecification` or an explicit price basis
   - `FAQPage` on genuine Q&A only
   - `Review` / `AggregateRating` **only** where first-party and policy-compliant — do not mark up third-party ratings you don't own
   - `Person` for named practitioners where relevant
   - `BreadcrumbList`, `WebSite`, `Organization`
3. **T12.3 Identity graph.** `sameAs` linking every claimed profile, registry entry, credential verification page, and professional body listing. This is the highest-leverage, lowest-effort GEO action available and it is almost universally skipped.
4. **T12.4 Coverage markup.** `areaServed` expressed with real geographic entities (place identifiers, postcodes, `GeoShape`), not prose. Only for evidenced areas.
5. **T12.5 Credential markup.** `hasCredential`, `identifier`, issuer, and a verification URL. Machine-verifiable trust is the coming differentiator in trades, health, legal, and financial services.
6. **T12.6 Consistency validation.** Automated diff: schema values vs. GBP values vs. on-page text vs. canonical record. Any divergence is a defect.
7. **T12.7 Answer-shaped content blocks.** On each key page, one clearly delimited passage that directly answers the page's primary question in 40–80 words, factually and without marketing hedging. Retrievers lift clean passages; hedged prose does not survive extraction.

**Metrics** `protocol.schema.type_coverage` · `protocol.schema.validity_rate` · `protocol.schema.content_match_rate` · `protocol.identity.sameas_count` · `protocol.credential.machine_verifiable_ratio`

**Automation class** Inventory, validation, and consistency diff: fully automate and run weekly. Deployment: assist.

---

## 4. W13 — Machine-readable feeds and endpoints

**Purpose** Make the business transactable by software, not just describable to it.

This is where almost no local business currently is, which is precisely why it is worth building now. It is a two-to-three-year lead, not a marginal gain.

**Readiness ladder** — assess and target one rung at a time:

| Rung | Capability | Typical state |
|---|---|---|
| 0 | Phone number and a contact form | Most local businesses |
| 1 | Complete, valid structured data + identity graph | Good agencies |
| 2 | Published service + price-basis + coverage in machine-readable form | Rare |
| 3 | Published availability (real, updating) | Very rare outside booking-platform verticals |
| 4 | Quote or booking endpoint callable by a third party | Almost nonexistent locally |
| 5 | Agent-facing interface with auth, capability description, and terms (e.g. an MCP server or documented API) | Frontier |
| 6 | Accepts verified-agent payment under a user mandate (UCP/ACP checkout, AP2 mandate, Visa TAP / Mastercard Agent Pay token) | Live for platform merchants (Shopify, Stripe) since 2026; rare for independents |

**Tasks**
1. **T13.1 Access policy audit.** What do `robots.txt`, WAF rules, bot-management, and CDN configuration actually do to AI crawlers and agent user-agents? Many businesses block the very retrievers they want to be cited by, entirely by accident via a default security setting. **Check this first — it is a five-minute check that can invalidate an entire GEO programme.** *(v2, Sep 2026)* Cloudflare now blocks Agent and Training crawlers by default on ad-displaying pages of new domains (from 15 Sep 2026). Check every new domain, and extend the audit to user-invoked agents (Meta Muse Secure VM, ChatGPT agent, Gemini) and payment-network-verified agents. See W15 in `geo-axo-strategist`.
2. **T13.2 Deliberate access decision.** Distinguish training crawlers, retrieval crawlers, and user-invoked agents. A defensible default for a local service business: allow retrieval and user-invoked agents, decide on training deliberately, document the decision. Write it down; clients will be asked about it.
3. **T13.3 Service and price feed.** A stable JSON or JSON-LD document listing services, price basis, coverage, and constraints. Even a static file at a documented URL puts the client on rung 2.
4. **T13.4 Availability signal.** Even coarse ("emergency cover today: yes; next standard slot: Thursday") beats silence, if it is genuinely maintained. **Stale availability is worse than none** — an agent that gets a wrong answer once deprioritises the source.
5. **T13.5 Quote/booking path.** Assess what exists. If there's a booking system, is it callable, or only clickable? Document the gap and cost the fix.
6. **T13.6 `llms.txt` or equivalent.** A concise, plain-language file describing what the business does, where, for whom, at what price basis, and how to engage. Adoption is not universal and the standard is unsettled — position it as cheap optionality, not a guaranteed win. Say that plainly to the client.
7. **T13.7 Agent-completability test.** Attempt the customer journey as an agent would: resolve entity → confirm coverage → confirm service → get a price → get availability → initiate booking. Record where it breaks. **This single test is the most persuasive artefact in the whole engagement** — a client watching an assistant fail to book them, live, understands the proposition instantly.

**Metrics** `protocol.readiness.rung` · `protocol.access.retriever_allowed` · `protocol.feed.freshness_hours` · `protocol.journey.completion_depth` (0–5, how far an agent gets)

**Automation class** Access audit and feed validation: automate. Journey test: assist, run monthly. Endpoint build: retain (engineering).

---

## 5. W14 — Answer-engine probing and citation share

**Purpose** Measure what generative systems actually say about the client and its competitors, over time.

Nobody has ground truth here, so **the method is the asset**. Discipline in probe construction is what turns anecdote into a time series.

**Probe set design**
Build 30–60 fixed prompts per client, held constant so results are comparable across runs. Cover the intent classes:

| Class | Example shape |
|---|---|
| Discovery | "Who does [service] in [area]?" |
| Comparison | "Compare the best [service] providers in [area]" |
| Constrained | "I need [service] in [area] this week, under [budget], [constraint]" |
| Eligibility | "Which [providers] in [area] are [licensed/accredited/24-hour]?" |
| Brand | "Is [client] any good?" / "What do people say about [client]?" |
| Transactional | "Book me [service] in [area] for [time]" |
| Adversarial | "Any complaints about [client]?" / "Cheapest [service] in [area]" |

Include the adversarial class. Discovering how a model characterises the client's weaknesses is often the most valuable output of the entire audit, and it is uncomfortable enough that competitors won't run it.

**Run protocol**
- Fixed engines list, fixed personas, fixed market and locale, fixed cadence (weekly for priority, monthly for full set).
- Fresh session per probe; no conversational carryover.
- Capture full response text plus every citation.
- Run ≥3 repetitions per probe per engine and record variance — **single-run results are noise**; the variance itself is a finding worth reporting.
- Log `engine_version_hint` and treat any step-change as a possible platform event, not a client performance event.

**Extraction per result**
`client_mentioned` · `client_rank_in_answer` · `competitors_mentioned[]` · `answer_shape` · `citations[]` with domain, ownership, and which claim each supports · characterisation sentiment · factual errors about the client.

**Derived metrics**
- `geo.mention_rate` — share of probes mentioning the client
- `geo.shortlist_rate` — share where the client is in a returned shortlist
- `geo.primary_rate` — share where the client is the single recommendation
- `geo.citation_rate` — share where a client-owned URL is cited
- `geo.third_party_grounding_share` — share of client-supporting citations from sources the client doesn't own. **This is the key GEO health metric.** High owned-only citation means the model is repeating your marketing; high third-party share means it has corroboration, which is far more durable and far harder for a competitor to replicate.
- `geo.factual_error_rate` — how often the model states something false about the client. Every instance is a remediation task at the Entity Layer.
- `geo.share_of_answer` — client mentions ÷ all provider mentions across the probe set. The generative analogue of share of voice, and the number to put on the front page of the report.

**Remediation loop**
Factual error → trace to the source the model most plausibly used → fix at source → re-probe after 2–4 weeks → log as a `ChangeEvent`. This loop is the single clearest demonstration of GEO value to a sceptical client, because it is visible, causal, and fast.

**Metrics governance** These are volatile, non-deterministic, and vendor-dependent. Always report with n, variance, and run date. Never present a single probe screenshot as a trend. Do not let a good week become a claim.

---

## 5b. v2 additions (Sep 2026)

Personal agents shipped at scale in 2026 (Meta Muse, Siri AI, Alexa for Shopping), commerce protocols went live (UCP, ACP, AP2), and payment networks now verify agents. The brand-level skill `geo-axo-strategist` holds the canonical model (`assets/knowledge.json`) and adds W15–W20. For local businesses, apply them like this:

- **W15 Agent access and identity:** allow retrieval and verified agents; stop CAPTCHAing booking agents.
- **W16 Agentic commerce rails:** booking platforms (OpenTable, Google Reserve, Expedia) are the local rails. Muse books through OpenTable; AI Mode books hotels directly.
- **W17 Agent surface coverage:** add Muse, Siri AI and Alexa to the fixed engines list in W14. Report per surface.
- **W19 Mandate equity:** repeat services (servicing, cleaning, grooming) become standing mandates. Structured rebooking wins the default.
- Probe engines list (v2): ChatGPT, Gemini/AI Mode, Meta Muse, Perplexity, Copilot, Alexa, plus Siri where scriptable.

## 6. The Agent Readiness Index

A single 0–100 score, five weighted components. Use it to open and close every engagement.

> **v2 note:** `geo-axo-strategist` defines ARI v2 with seven components (Access split from Feeds, plus Mandate equity). Use v2 for new engagements. Keep v1 for clients already baselined on it, and report both for one cycle when migrating.

| Component | Weight | What it measures |
|---|---|---|
| **Entity resolvability** | 25 | NAP consistency, claimed-profile coverage, `sameAs` graph, duplicate freedom, credential verifiability |
| **Claim legibility** | 20 | Schema coverage and validity, content-match, answer-shaped passages, price and coverage explicitness |
| **Third-party corroboration** | 25 | Review corpus depth and freshness, service × area coverage in review text, independent citations, directory and body listings |
| **Access and feeds** | 15 | Retriever access, feed presence and freshness, availability signal, `llms.txt` |
| **Transactability** | 15 | Agent journey completion depth, quote/booking callability, response latency |

Weighting rationale: resolvability and corroboration dominate because they are what a model can least easily fake or infer, and what a competitor can least easily copy. Re-tune weights annually against your own `EffectEstimate` data, and document the change.

**Reporting rule:** report the index *with its components*. A single number invites gaming; the component profile drives the backlog.

---

## 7. Sequencing GEO/AXO against classical work

Do not sell this as a replacement. Sell it as the part of the work that keeps paying.

| Horizon | Emphasis | Rationale |
|---|---|---|
| **0–3 months** | Entity + eligibility fixes, review velocity, GBP completeness | Fastest observable effect; also the foundation of every GEO metric |
| **3–9 months** | Schema, identity graph, evidenced coverage pages, probe baseline and remediation loop | Compounding; establishes the time series before competitors have one |
| **9–24 months** | Feeds, availability, booking callability, agent interfaces | Where the lead is built; low competition now, high switching cost later |

The honest framing for the client: *the map pack work has a known, decaying return; the entity and protocol work has an uncertain but growing return, and it is cheap to do now and expensive to retrofit.* That is a real argument, not a scare story, and it holds up if the trend reverses — none of the entity or protocol work is wasted in a world where classical search persists.

---

## 8. What we do not claim

Written explicitly so it survives into client conversations:

- We cannot guarantee inclusion in any AI answer. There is no submission mechanism and no ranking API.
- We do not know the weighting any engine applies. Every causal claim we make is inference from our own change-event data, and is graded.
- `llms.txt` and similar conventions are unsettled. We do them because they are cheap, not because they are proven.
- Probe results are non-deterministic. We report distributions, not screenshots.
- Anyone selling guaranteed GEO placement is selling something that does not exist.

This section is a competitive asset. In a market filling with confident nonsense, documented epistemic discipline is a differentiator that closes deals with sophisticated buyers.
