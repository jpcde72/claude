---
name: local-discovery-os
description: Run a productised local-discovery service — Google Business Profile optimisation, local website architecture, and forward-looking GEO (generative engine optimisation) and AXO (agentic experience optimisation) readiness. Use whenever the user asks to audit a Google Business Profile, analyse local competitors or the map pack, build service+city pages, run a keyword gap or Search Console analysis, plan review or posting cadence, assess whether a business is retrievable or transactable by AI assistants and shopping agents, or productise any of this into a repeatable multi-client service. Trigger on "GBP audit", "local SEO", "map pack", "service area pages", "near me", "review velocity", "GEO audit", "AI Overviews visibility", "agent readiness", "will an AI recommend us", or any request to turn local visibility work into a documented, automatable, benchmarkable operating system. Always use it even if the user names only one tactic — it supplies the shared ontology, evidence rules and benchmark model.
---

# Local Discovery Operating System (LDOS)

A three-layer operating system for making a business **findable, choosable, and transactable** — by humans in a map pack today, and by generative engines and buying agents tomorrow.

This skill converts a loose collection of local-SEO tactics into a service: a fixed ontology, a repeatable audit-to-action pipeline, a governed automation cadence, and a cross-client benchmark base that improves with every engagement.

---

## 1. The core reframe (read this before doing anything)

Most local-SEO material optimises for **a position in a ranked list rendered to a human**. That destination is dissolving. Increasingly the buyer is an assistant or agent that resolves an entity, retrieves claims about it, checks eligibility, and returns one or three options — or completes the job outright.

So LDOS optimises three layers, not one ranking:

| Layer | Question it answers | Optimised for | Failure mode |
|---|---|---|---|
| **Entity Layer** | *Who is this business, unambiguously?* | Machine resolution: one canonical, consistent, verifiable identity across every surface | Entity ambiguity — the agent can't tell if you're one business, three, or closed |
| **Surface Layer** | *Where does the entity get rendered, and how fresh is it?* | Coverage, freshness, evidence density on GBP, organic, AI answers, directories, review platforms | Invisible or stale on the surface the buyer actually used |
| **Protocol Layer** | *Can a non-human buyer complete the job?* | Structured availability, pricing, coverage polygons, booking and quote endpoints, machine-readable proof | Recommended but not transactable — the agent routes to whoever can be booked |

Cross-cut every layer with the **Decision Policy** arenas — these are what an engine or agent is actually running:

- **Eligibility** — may this business be included at all? (categories, verified service area, licensing, hours, capacity, entity resolution)
- **Justification** — why this one over the near-identical alternative? (evidence, specificity, recency, corroboration across sources)
- **Defaults** — what gets returned when the user expresses no preference? (the shortlist, the "book it" pick)

Every task in this skill must declare which layer and which arena it serves. If a task serves none, cut it.

---

## 2. When to use which reference

Do not load everything. Load what the current phase needs.

| You are doing | Read |
|---|---|
| Setting up a new client, defining what data you hold | `references/ontology.md` |
| Running any audit or building any deliverable | `references/workstreams.md` |
| Anything about AI answers, agents, schema, feeds, retrievability | `references/geo-axo.md` |
| Cadence, triggers, drift detection, what to automate | `references/automation.md` |
| Scoring, thresholds, cross-client comparison, learning | `references/benchmarks.md` |
| Consent, tenancy, PII, credentials, client separation | `references/governance.md` |
| Building the product around the skill | `references/platform-architecture.md` |
| Machine-readable data contracts | `assets/*.schema.json` |
| Brand-level agentic work, Muse / Siri / Alexa / ChatGPT agents, 2027 planning, ARI v2 | the `geo-axo-strategist` skill (`assets/knowledge.json`) |

---

## 3. The pipeline

Nine phases. Phases 0–1 happen once per client. Phases 2–5 are the engagement. Phases 6–8 are what makes it a service rather than a project.

### Phase 0 — Engage and govern
Before touching a single surface, establish the tenancy record. Read `references/governance.md`.

- Create the `Client` and `Location` records; assign `tenant_id`.
- Record consent scope: which properties may be accessed, which data may contribute to cross-client benchmarks (default: **aggregated only, never raw**).
- Record credential handles — never credential values — for GBP, Search Console, analytics, rank tools.
- Agree the measurement baseline date and the reporting cadence.
- Declare what you will **not** do (no review gating, no fake locations, no doorway pages, no scraped content). Write it down; it is a selling point and a liability shield.

**Exit test:** a second operator could pick up this client with no verbal handover.

### Phase 1 — Canonicalise the entity
Replace the "paste your business details" habit with a validated record. Read `references/ontology.md` and use `assets/client_entity.schema.json`.

Populate: legal and trading name, NAP, coordinates, GBP CID/place ID, licence and credential numbers, founding date, service catalogue, service-area geometry, capacity constraints, price bands, languages, payment and booking methods, competitor set, target keyword set, and current standings.

Then run **entity resolution**: search the business across GBP, Bing Places, Apple Business Connect, Yelp, sector directories, Companies House / equivalent registry, and two major assistants. Record every variant of name, address, phone, hours, and category found. Every inconsistency is an Entity Layer defect and blocks Eligibility.

**Exit test:** one canonical record, an inconsistency register, and a confidence score per field.

### Phase 2 — Observe
Collect evidence. Never assert; always observe, timestamp, and attribute. Every fact becomes an `Observation` with `source`, `observed_at`, `method`, and `confidence`. Read `references/workstreams.md` for the eleven observation workstreams (W1–W11).

Rules:
- Same method for client and competitors, same day, same location context — otherwise the comparison is noise.
- Localise the observation (geo context matters enormously for map results); record the location context used.
- Snapshot raw output. Diffing snapshots over time is where the durable insight lives.
- Where a value can't be observed reliably (upload dates, engagement, exact spend), mark it `estimated` with the estimation method — never launder an estimate into a fact.

### Phase 3 — Diagnose
Convert observations into scored gaps against `references/benchmarks.md`.

Each gap gets: layer, decision-policy arena, gap size vs. competitor median, confidence, and whether it is **structural** (needs a build) or **operational** (needs a cadence).

Diagnosis rule: a gap only counts if you can name the query, prompt, or agent decision it loses you.

### Phase 4 — Prescribe
Produce a single ranked backlog, not a set of reports. Each item carries:

`recommendation_id · layer · arena · action · expected_effect · impact (H/M/L) · effort (H/M/L) · latency (days to observable effect) · owner · evidence_ref · verification_method`

Latency bands to use consistently: **0–7d** (profile fields, categories, attributes, descriptions), **7–30d** (posts, photos, review cadence, title/meta), **30–90d** (new pages, internal linking, citation cleanup), **90d+** (authority, review corpus depth, third-party corroboration).

State uncertainty explicitly. Category and attribute changes have well-observed fast effects; several widely repeated claims in local-SEO folklore do not survive scrutiny — see the "contested claims" section of `references/benchmarks.md` and label anything resting on them as *hypothesis*, not *finding*.

### Phase 5 — Produce
Generate the artefacts: category/attribute change list, service descriptions, profile description variants, post calendar, photo shot list and naming convention, review-response system, service+city page specs and copy, title/meta rewrites, internal link plan.

House rules for all generated copy:
- Write for a human reader first; a passage that only makes sense as a ranking signal will be discounted by both readers and models.
- Every claim in client-facing copy must map to something true in the entity record. If the record doesn't support it, don't write it.
- Specificity is the ranking asset that generalises: named neighbourhoods, named processes, real constraints, real prices, real timescales.

### Phase 6 — Agent-proof (GEO/AXO)
The differentiator. Read `references/geo-axo.md` and run the Agent Readiness Audit.

Covers: structured data completeness and validity, entity graph consistency, machine-readable service/price/availability feeds, crawler and agent access policy, retrieval probes against assistants, citation share, answer-shortlist presence, and transactability (can an agent actually book, quote, or hold a slot?).

**Exit test:** a documented probe set with results, and a scored Agent Readiness index with the three cheapest moves to raise it.

*v2 (Sep 2026):* add the agentic workstreams W15–W19 (access and identity, commerce and booking rails, per-surface coverage, brand endpoint, mandate equity) from `geo-axo-strategist`, and score ARI v2.

### Phase 7 — Measure and attribute
Fix the metric spine before the first change ships. Read `references/benchmarks.md`.

Track by layer: entity consistency score; surface coverage, freshness, review velocity, position distribution, impression/click split, discovery-vs-branded split; protocol readiness score, probe citation rate, agent-completable actions. Tie to business outcome: qualified enquiries, booked jobs, revenue per job.

Use change-log-anchored analysis: every shipped change is a dated event; read metric movement against those events rather than against a calendar month.

### Phase 8 — Maintain, automate, learn
Read `references/automation.md`.

Decide per task: **automate** (deterministic, high frequency, low judgement), **assist** (agent drafts, human approves), or **retain** (judgement-dense, client-facing, risk-bearing). The automation frontier moves; the governance work does not. Re-run the classification quarterly.

Then contribute to the benchmark base per `references/benchmarks.md` — aggregated, anonymised, sector- and market-tagged. This is the asset that makes engagement N+1 cheaper and better than engagement N.

---

## 4. Standing rules

1. **Observation before assertion.** Every number in a client deliverable traces to a timestamped observation or a labelled estimate.
2. **One ontology.** Never invent ad-hoc field names. If the schema lacks a field, extend the schema deliberately and version it.
3. **Layer and arena tagging is mandatory** on every gap, recommendation, and task.
4. **Uncertainty is stated, not smoothed.** "I don't know" is an acceptable and expected output.
5. **No tactic that would embarrass the client if published.** Review gating, fabricated locations, and cloaked content are out of scope permanently.
6. **Comparability over completeness.** A narrower audit run identically across clients is worth more than a rich bespoke one, because only the former builds benchmarks.
7. **Write for the reader and the retriever.** Content optimised solely for extraction reads badly and is increasingly discounted; content optimised solely for prose isn't retrievable. Do both.

---

## 5. Anti-patterns

- Running all workstreams at once. Sequence: entity → eligibility → justification → defaults → protocol.
- Treating competitor parity as the goal. Parity gets you eligible; only asymmetry gets you chosen.
- Optimising the map pack while the entity record is inconsistent. The foundation defect nullifies the tactic.
- Selling report volume. Sell the ranked backlog, the shipped changes, and the movement.
- Assuming today's automation boundary is permanent — or that a task, once automatable, still needs a human wrapper for its own sake.
