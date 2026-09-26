# LDOS Workstreams

Each workstream is specified as: **purpose · layer · arena · inputs · tasks · outputs · metrics · automation class · failure modes · agent extension**.

Run in the order given. The sequence is not arbitrary: eligibility defects nullify justification work, and justification work is wasted if the entity can't be resolved.

## Contents

**Entity Layer**
- W1 Entity resolution and consistency
- W2 Category architecture
- W3 Attribute and filter coverage
- W4 Service catalogue and coverage geometry

**Surface Layer**
- W5 Review corpus and velocity
- W6 Review response system
- W7 Freshness: posts and photos
- W8 Profile narrative (description and services copy)
- W9 Query and keyword gap
- W10 Owned-page performance and page-2 recovery
- W11 Local page architecture (service × city)

**Protocol Layer**
- W12 Structured data and entity graph
- W13 Machine-readable feeds and endpoints
- W14 Answer-engine probing and citation share

*(W12–W14 are specified in `geo-axo.md`; summarised here for sequencing only.)*

---

# ENTITY LAYER

## W1 — Entity resolution and consistency

**Purpose** Establish that the business resolves to exactly one unambiguous entity everywhere it appears.
**Layer** Entity · **Arena** Eligibility
**Why first** Every downstream tactic is multiplied by this. A duplicate listing, a legacy phone number on a directory, or a name variant on a review platform degrades both classical local ranking and model-side entity confidence.

**Inputs** Client record (Phase 1), location list, credential list.

**Tasks**
1. **T1.1 Canonical record lock.** Freeze the single true NAP, hours, name form. One string per field. Record the decision, not just the value.
2. **T1.2 Surface sweep.** Locate the business on: GBP, Bing Places, Apple Business Connect, Yelp/local equivalent, top 10 sector directories for the market, registry (Companies House/equivalent), Facebook, industry bodies. Record `profile_url`, claimed status, and displayed NAP.
3. **T1.3 Variance register.** Diff every displayed value against canonical. Classify each as `name_variant`, `phone_variant`, `address_variant`, `hours_conflict`, `category_conflict`, `unclaimed`, `duplicate_suspected`, `closed_flag_risk`.
4. **T1.4 Duplicate hunt.** Search by phone, by address, by former trading name, by practitioner name. Duplicates suppress and confuse.
5. **T1.5 Credential verification.** For each credential, capture the issuer's own verification URL. Anything not externally verifiable is marked `self_declared` and treated as weak.
6. **T1.6 Consistency score.** `entity.consistency.nap_variance` = 1 − (variant fields ÷ (fields × profiles)). Report per surface and overall.

**Outputs** Canonical record · variance register · duplicate list · remediation backlog with surface owner and access path.

**Metrics** `entity.consistency.nap_variance` · `entity.coverage.claimed_profiles` · `entity.credential.verifiable_ratio`

**Automation class** Sweep: automate. Variance classification: assist. Remediation: retain (each surface has different claim/verification friction).

**Failure modes** Treating this as one-off (it drifts — aggregators re-inject stale data); fixing the visible surface while leaving the upstream data aggregator wrong; closing duplicates in a way that loses their review corpus.

**Agent extension** Publish `sameAs` links across every claimed profile plus registry and credential URLs. This is how a model builds confidence that six sources describe one business rather than several.

---

## W2 — Category architecture

**Purpose** Ensure the profile is eligible for every search where the business can genuinely serve.
**Layer** Entity · **Arena** Eligibility
**Why it matters** Categories are a hard filter, not a soft signal. Wrong primary category is the single highest-leverage defect in local search, and it is usually set once at listing creation and never revisited.

**Inputs** Service catalogue with `margin_rank` / `demand_rank`; competitor set; target query set.

**Tasks**
1. **T2.1 Pack observation.** For each of the top target queries (recommend 8–15, not 3), run a localised map search from a fixed point set. Record the full pack, positions, and the query's SERP feature set. Repeat from 3+ points per priority area — a single-point observation is not a ranking, it is an anecdote.
2. **T2.2 Competitor category extraction.** For every business appearing in any observed pack, extract primary and secondary categories. Include businesses ranked 4–10, not just the top 3 — the pack rotates.
3. **T2.4 Frequency and lift analysis.** Compute, per category: how many observed competitors hold it, its co-occurrence with high-rank positions, and whether it appears more often among top-3 than 4–10 holders. Frequency alone is descriptive; the top-3 skew is the interesting signal.
4. **T2.5 Eligibility mapping.** For each candidate category, ask: does the client genuinely and lawfully perform this? Reject anything false. Category stuffing is a suspension risk and, more importantly, produces enquiries you can't service.
5. **T2.6 Primary category decision.** Test the primary against the highest-value query cluster, not the broadest one. Model the trade-off explicitly: the primary category shapes eligibility for the whole profile.
6. **T2.7 Change plan.** Sequence changes one at a time with ≥14 days between primary-category changes, each logged as a `ChangeEvent`, so effect is attributable.

**Outputs** Category comparison matrix (one tab per query) · ranked add list segmented into *held by all competitors* (parity), *held by majority* (strong), *held by one* (differentiation) · primary-category recommendation with rationale · sequenced change plan.

**Metrics** `entity.category.parity_gap` · `entity.category.top3_skew_captured` · `surface.map.pack_presence_rate`

**Automation class** T2.1–T2.4 automate; T2.5–T2.7 retain.

**Failure modes** Copying competitor categories without eligibility checking; changing primary and three secondaries in one day and learning nothing; observing from one location and mistaking proximity effects for category effects.

**Agent extension** Map every held category to the equivalent `schema.org` type and to the client's own service taxonomy. Category is a platform-specific string; the durable asset is the mapping table between platform taxonomies, your canonical service names, and schema types — that mapping is what survives when a fourth taxonomy appears.

---

## W3 — Attribute and filter coverage

**Purpose** Capture the refinement filters and trust tags that gate inclusion under qualified searches.
**Layer** Entity · **Arena** Eligibility + Justification

**Tasks**
1. **T3.1** Extract the full attribute set displayed on the client profile and every competitor profile. Include the ones surfaced only in the filter UI, not just those rendered on the listing.
2. **T3.2** Separate **filter attributes** (gate inclusion under a refinement — e.g. accessibility, appointment requirement, opening state, payment types) from **trust attributes** (change choice — e.g. ownership identity, guarantee, free estimate). Different priority logic.
3. **T3.3** Verify truthfully. Every attribute is a claim you will be held to.
4. **T3.4** Identify attributes the client can *become* eligible for cheaply (adding a payment method, publishing a genuine estimate policy) — this is an operational change disguised as an SEO change, and it is often the highest-ROI item in the whole audit.
5. **T3.5** Produce the three-tier list: universal (immediate), majority (strong), singleton (differentiation).

**Outputs** Attribute matrix · tiered add list with eligibility/justification tags · operational change requests.

**Metrics** `entity.attribute.parity_gap` · `entity.attribute.filter_coverage`

**Automation class** Extraction: automate. Verification and operational change: retain.

**Agent extension** Attributes are the most direct analogue of what an agent filters on. Mirror every true attribute into structured data and into the client's own machine-readable profile, so eligibility survives outside the platform that hosts the attribute.

---

## W4 — Service catalogue and coverage geometry

**Purpose** Make the full, true service and coverage set legible on every surface.
**Layer** Entity · **Arena** Eligibility

**Tasks**
1. **T4.1** Extract the services section from client and competitor profiles: service names, presence of descriptions, description structure, word counts.
2. **T4.2** Cross-reference against the client's website and against the internal service catalogue. Three-way diff. The common defect: a service is performed and sold, appears on the website, and is absent from the profile — so it is invisible in map results entirely.
3. **T4.3** Classify each service as universal (all competitors list it), contested (some), or unique.
4. **T4.4** Declare service areas: type, geometry, and crucially `is_evidenced`. For each declared area, list the evidence (completed jobs, reviews mentioning it, physical proximity, staff based there).
5. **T4.5** Flag over-declaration. Declaring 40 towns you cannot evidence weakens every one of them.
6. **T4.6** Write service descriptions (see Production rules below).

**Outputs** Service comparison matrix · three-way diff · evidenced coverage map · description set.

**Metrics** `entity.service.profile_site_coverage` · `entity.service.description_completeness` · `entity.area.evidenced_ratio`

**Automation class** Extraction and diff: automate. Coverage declaration: retain.

**Agent extension** The evidenced-coverage map is a genuinely differentiated asset. Expose it as structured `areaServed` plus, ideally, a machine-readable coverage file. An agent asked "who covers this postcode?" wants a resolvable answer, not a marketing claim.

---

# SURFACE LAYER

## W5 — Review corpus and velocity

**Purpose** Understand the evidence base competitors have accumulated, and set a velocity and content target.
**Layer** Surface · **Arena** Justification

**Tasks**
1. **T5.1** For client and each competitor: total count, mean rating, distribution across 1–5.
2. **T5.2** Velocity: reviews in trailing 30 / 60 / 90 / 365 days. Compute `reviews_per_month_trailing_90` and the trend. A large stale corpus is weaker than a smaller live one, both for platform freshness signals and for a model summarising "recent customer experience".
3. **T5.3** Content extraction from the most recent 50 reviews per competitor: services named, places named, staff named, outcome language, recurring praise, recurring complaint themes.
4. **T5.4** Complaint theme analysis on competitors — this is competitive positioning intelligence, not just SEO. Recurring competitor complaints are your justification copy.
5. **T5.5** Own-corpus gap: which services and areas are *absent* from your review text? Those are the ones a model has no third-party evidence for.
6. **T5.6** Velocity target = max(competitor p75 velocity, current × 1.5), with an explicit, ethical acquisition mechanism (post-job request, timed, single ask, no incentive, no gating, no filtering by expected sentiment).
7. **T5.7** Customer prompt guidance: a short natural request that invites customers to mention what they had done and where. Guidance, never a script — dictated reviews read as dictated, and platforms act on solicitation patterns.

**Outputs** Review comparison matrix · theme analysis · content gap by service × area · velocity target · acquisition SOP.

**Metrics** `surface.review.velocity_30d` · `surface.review.recency_median_days` · `surface.review.service_coverage` · `surface.review.area_coverage` · `surface.review.sentiment_theme_index`

**Automation class** Extraction and theming: automate. Acquisition design: retain. **Never automate** anything that shapes which customers are asked.

**Failure modes** Optimising rating mean (it barely moves and barely matters above ~4.3); gating; incentivising; asking in bulk after a quiet period, which produces a spike pattern that is both detectable and unconvincing.

**Agent extension** Review *text* is the richest third-party evidence a model has about a business. Coverage of your service × area matrix in review language is a direct GEO input — it is the corpus that gets summarised when someone asks an assistant "who's good for X in Y?". Track `surface.review.service_coverage` as a first-class GEO metric, not a vanity one.

---

## W6 — Review response system

**Purpose** Convert responses into a consistent, human, evidence-adding layer.
**Layer** Surface · **Arena** Justification

**Tasks**
1. **T6.1** Benchmark response rate, median response latency, response length, tone, and whether responses add information.
2. **T6.2** Analyse competitor handling of negative reviews. Defensive responses are a competitive gift; note them.
3. **T6.3** Build a response *system*, not templates alone: a decision tree (5★ / 4★ / 3★ / 1–2★ / factual dispute / safety or legal issue / suspected fake), 3 variants per branch, and an escalation rule for anything involving injury, legal threat, or an employee.
4. **T6.4** Each variant: 40–80 words, references what was done and where when the review supports it, one specific detail, no boilerplate opener, no keyword stuffing.
5. **T6.5** Set response SLA (target: <48h; <24h for negative) and a weekly review.

**Outputs** Response benchmark table · decision tree · variant library · escalation policy · SLA.

**Metrics** `surface.review.response_rate` · `surface.review.response_latency_median_hours` · `surface.review.response_specificity`

**Automation class** Assist. Draft with a model, human approves every response without exception. Fully automated responses are detectable, and a wrong automated response to a serious complaint is a material reputational event.

**Honesty note** Responding is confirmed good practice and clearly affects reader perception and conversion. The claim that responses directly lift ranking is widely repeated and weakly evidenced — treat as `hypothesis` in `impact_basis`, and justify the work on conversion and evidence-density grounds, which are solid.

**Agent extension** Responses are owned text attached to third-party evidence. Where a review names a service and area, a response confirming specifics creates a corroborated pair — exactly the structure a retrieval system can use.

---

## W7 — Freshness: posts and photos

**Purpose** Sustain activity signals and build a visual evidence base.
**Layer** Surface · **Arena** Justification + Defaults

**Tasks**
1. **T7.1** Observe competitor posting: count over 90 days, cadence, types, CTA use, imagery, themes, seasonal patterns.
2. **T7.2** Observe photo estate: total count, upload recency, type mix (team / job site / before-after / vehicles / equipment / premises / completed work), professional vs. phone, apparent stock imagery, presence of people, recognisable local context.
3. **T7.3** Set cadence targets. Posts: 2–3/week. Photos: 3–5/week sustained. **Consistency over volume** — a burst followed by silence is worse than a steady trickle.
4. **T7.4** Build an 8-week calendar mixing: seasonal service, project showcase with before/after, area-specific posts, review highlights, team, and problem-explainer content. Every post: 100–150 words, one target concept, a real CTA, and a described image so the client knows what to photograph.
5. **T7.5** Photo shot list per week with location, subject, and purpose. Naming convention: `{service}-{area}-{yyyymm}-{n}.jpg`. Include capture guidance (real jobs, consented people, no identifiable customer property without permission, no stock).
6. **T7.6** Geo-context guidance: photograph work in the areas you claim to serve. This is the cheapest form of coverage evidence there is.

**Outputs** Cadence benchmark · 8-week calendar (weeks 1–4 full copy, 5–8 outlines) · shot list · naming and consent SOP.

**Metrics** `surface.freshness.post_cadence_7d` · `surface.freshness.photo_cadence_7d` · `surface.freshness.days_since_last_activity` · `surface.evidence.area_photo_coverage`

**Automation class** Post drafting: assist. Scheduling: automate. Photography: retain (client-side).

**Honesty note** The frequently quoted "photos drive 42% more direction requests / 35% more clicks" figure originates from old vendor-sourced platform marketing material and is not a controlled result. Use it as directional colour at most; never as a projection in a client deliverable. Justify photo work on evidence-building and conversion grounds.

**Agent extension** Photos with real captions, filenames, and structured `image` references give a multimodal retrieval system something to work with. As assistants increasingly render visual answers, an estate of real, well-labelled, area-specific work photos becomes a retrieval asset rather than decoration.

---

## W8 — Profile narrative (description and services copy)

**Purpose** Own the text you fully control.
**Layer** Surface · **Arena** Justification

**Tasks**
1. **T8.1** Extract competitor descriptions: full text, length, concepts covered, areas named, trust signals, CTA, tone.
2. **T8.2** Identify: what every competitor says (table stakes), what none says (ownable ground), what you say that is genuinely distinctive.
3. **T8.3** Draft three variants — ranking-weighted, conversion-weighted, trust-weighted — each within the platform character limit, each true, each readable aloud without embarrassment.
4. **T8.4** Define the test: run one variant for a fixed window, hold everything else constant, log as a `ChangeEvent`, read impressions/actions against it. This is the discipline that turns copy into an asset.
5. **T8.5** Service descriptions: 40–60 words each, naming the service, one real area, one concrete outcome or constraint, in plain language.

**Outputs** Description comparison table · three variants · test plan · full service description set.

**Metrics** `surface.profile.description_completeness` · `surface.profile.distinctiveness_index` · `surface.map.action_rate`

**Automation class** Assist.

**Caution** A/B inference on profile descriptions is weak: no holdout, high external variance, seasonality. State the limitation. Sequential testing with a long window and a stable baseline is the honest method, and even then read it as directional.

**Agent extension** Write descriptions that answer a question rather than list keywords. Retrieval favours passages that resolve an intent cleanly. "We provide same-day boiler repair across [area] with parts held in van, typically within four hours" is both better copy and better retrievable evidence than a keyword string.

---

## W9 — Query and keyword gap

**Purpose** Find demand competitors capture and the client does not.
**Layer** Surface · **Arena** Defaults

**Tasks**
1. **T9.1** Pull the keyword gap between client and 3–5 competitor domains from the available rank tool. Filter to competitor positions 1–20 where the client is absent.
2. **T9.2** Apply the local-intent filter: volume band appropriate to the market (in a small market, 20–200/mo is the real sweet spot — do not import a US volume threshold into a UK town), difficulty below a threshold calibrated to the client's authority, and presence of a local, urgent, comparative, or proximity modifier.
3. **T9.3** For every surviving query, observe the actual SERP: is there a local pack, an AI answer, a marketplace occupying the top slots? A #1 organic position beneath an AI answer and a pack is worth a fraction of what the volume implies. **This step is what separates a 2026 audit from a 2019 one.**
4. **T9.4** Map each query to an existing page (optimise) or no page (create).
5. **T9.5** Score opportunity: `(volume × intent_weight × realistic_ctr_given_serp) ÷ difficulty`, where `realistic_ctr_given_serp` is discounted by AI answer and pack presence.
6. **T9.6** Deduplicate against W11 so page creation is planned once.

**Outputs** Gap sheet sorted by opportunity score, with SERP-feature column and Action Required (optimise / create / ignore-because-SERP).

**Metrics** `surface.organic.gap_count` · `surface.organic.addressable_volume` · `surface.serp.ai_answer_incidence`

**Automation class** Automate pulls and filters; retain the SERP-shape judgement.

**Agent extension** `surface.serp.ai_answer_incidence` per query cluster is the leading indicator of where classical ranking value is decaying. Track it as a time series per client and per sector — this is one of the most valuable cross-client benchmarks you can build, and almost nobody is building it.

---

## W10 — Owned-page performance and page-2 recovery

**Purpose** Convert existing near-miss rankings into visibility.
**Layer** Surface · **Arena** Defaults

**Tasks**
1. **T10.1** Export 90 days of query × page performance from Search Console.
2. **T10.2** Segment: branded vs. discovery (the single most important split, and the one most agency reports omit); positions 1–3, 4–10, 11–20, 20+.
3. **T10.3** Isolate the recovery set: position 11–20 with meaningful impressions. Rank by `impressions × plausible_ctr_gain`.
4. **T10.4** For each recovery page, inspect: keyword in title, in H1, in first 100 words, word count, internal inlink count and anchor text, meta description quality, content freshness, and whether the page actually answers the query's intent.
5. **T10.5** Identify cannibalisation: one query splitting across multiple pages, or the wrong page ranking. Resolve by consolidation or intent separation, not by adding more pages.
6. **T10.6** Identify high-impression low-CTR pages: a title/meta problem, not a ranking problem, and the fastest measurable win available.
7. **T10.7** Build a 30-day sprint: week 1 titles/H1s, week 2 thin-content expansion, week 3 internal links, week 4 meta rewrites. Write the actual copy, not instructions.

**Outputs** Query×page matrix · recovery set · cannibalisation register · 30-day sprint with final copy · change log entries.

**Metrics** `surface.organic.position_distribution` · `surface.organic.discovery_click_share` · `surface.organic.ctr_vs_position_curve_delta`

**Automation class** Export, segmentation, and candidate identification: automate. Copy: assist. Consolidation decisions: retain.

**Caution** Search Console position is a smoothed average across contexts and is a weak per-page truth. Read the direction, not the decimal. Also note impressions increasingly include AI-answer contexts where a click was never available — a falling CTR at stable position may reflect SERP shape, not page quality. Say so in the report.

---

## W11 — Local page architecture (service × city)

**Purpose** Build a page estate that earns eligibility for area-qualified demand without generating thin duplication.
**Layer** Surface · **Arena** Defaults

**Tasks**
1. **T11.1** Inventory existing service, city, and service×city pages. Map to the evidenced-coverage set from W4.
2. **T11.2** Prioritise the matrix by `demand_rank × margin_rank × evidenced_coverage`. **Build only where evidence exists.** An unevidenced city page is thin content with a postcode in it, and it is the most common way local sites acquire a quality problem.
3. **T11.3** For each page, define the spec: URL slug, title (<60 chars), meta (<155), H1, opening that addresses the specific situation of someone in that area, an area-specific section grounded in real local facts (housing stock, common infrastructure, travel constraints, genuine local conditions), a process/what's-included section, local proof (reviews, jobs, photos from that area), 3 area-relevant FAQs, and a CTA reflecting real availability.
4. **T11.4** Differentiation test: strip the place name from two pages. If they are now indistinguishable, the pages are duplicates and should be a single hub with genuine sub-pages only where evidence justifies.
5. **T11.5** Internal linking: hub-and-spoke from the service hub, cross-links between adjacent areas, contextual links from proof content. Specify exact source pages and anchors.
6. **T11.6** Rollout cadence: publish in batches with a gap, so effect is attributable and quality stays high.

**Outputs** Coverage matrix · prioritised build list · per-page specs and copy · internal link plan · rollout schedule.

**Metrics** `surface.site.page_coverage_ratio` · `surface.site.differentiation_index` · `surface.site.thin_page_count`

**Automation class** Spec generation: assist. Local-fact research: assist with mandatory verification. Publication: automate. **The differentiation test is retained** — it is the quality gate that keeps this from becoming a doorway-page factory.

**Agent extension** Structure each page so a retriever can lift a clean answer: a direct answer paragraph near the top, explicit coverage statement, explicit price basis, explicit availability, `LocalBusiness` + `Service` + `FAQPage` schema, and a stable URL. Then verify by probe (W14) that assistants can actually retrieve and correctly attribute the coverage claim.

---

# PROTOCOL LAYER

Specified in full in `geo-axo.md`.

- **W12 Structured data and entity graph** — schema completeness, validity, `sameAs` graph, credential and coverage markup.
- **W13 Machine-readable feeds and endpoints** — service/price/availability feeds, booking and quote endpoints, agent access policy, MCP exposure.
- **W14 Answer-engine probing and citation share** — fixed probe set, run cadence, mention and citation tracking, third-party grounding share, shortlist presence.

---

# Production rules (apply to every generated artefact)

1. **Truth check before style check.** Every claim maps to a field in the entity record.
2. **Read it aloud.** If it sounds like it was written for a machine, rewrite it. Both humans and current models discount that register.
3. **Specificity is the strategy.** Named areas, named processes, real prices, real timescales, real constraints. Generic copy is unrankable, unquotable, and unpersuasive simultaneously.
4. **One idea per artefact.** Posts, descriptions, and FAQ answers that try to cover everything cover nothing.
5. **Answer-first structure.** Lead with the resolution, then the detail. Good for skim-readers, good for retrieval.
6. **Every artefact carries `generated_by` and `approved_by`.** No exceptions.
7. **No claim of guaranteed ranking outcomes.** Ever, in any artefact, including internal ones.
