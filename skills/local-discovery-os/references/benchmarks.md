# Metrics, Scoring and Benchmarks

The controlled vocabulary, the scoring model, and the rules that make cross-client learning legitimate.

---

## 1. Metric key vocabulary

Format: `{layer}.{surface_class}.{concept}.{qualifier}`. Controlled — never free text.

### Entity layer
| Key | Definition | Direction |
|---|---|---|
| `entity.consistency.nap_variance` | 1 − (variant fields ÷ total fields observed across profiles) | ↑ |
| `entity.coverage.claimed_profiles` | Claimed and verified profiles ÷ relevant surfaces for sector+market | ↑ |
| `entity.duplicate.count` | Suspected duplicate listings | ↓ |
| `entity.category.parity_gap` | Categories held by ≥2 pack competitors that client lacks | ↓ |
| `entity.category.top3_skew_captured` | Share of categories over-represented in top-3 that client holds | ↑ |
| `entity.attribute.parity_gap` | As above, attributes | ↓ |
| `entity.attribute.filter_coverage` | Filter-type attributes held ÷ applicable | ↑ |
| `entity.service.profile_site_coverage` | Services on profile ÷ services genuinely offered | ↑ |
| `entity.area.evidenced_ratio` | Evidenced areas ÷ declared areas | ↑ |
| `entity.credential.verifiable_ratio` | Externally verifiable credentials ÷ claimed | ↑ |

### Surface layer
| Key | Definition | Direction |
|---|---|---|
| `surface.map.pack_presence_rate` | Observations where client appears in pack ÷ total pack observations | ↑ |
| `surface.map.mean_position` | Mean pack position when present (report with presence rate, never alone) | ↓ |
| `surface.map.action_rate` | Profile actions ÷ profile views | ↑ |
| `surface.review.velocity_30d` | New reviews in trailing 30 days | ↑ |
| `surface.review.recency_median_days` | Median age of trailing-20 reviews | ↓ |
| `surface.review.service_coverage` | Services named in review text ÷ services offered | ↑ |
| `surface.review.area_coverage` | Areas named in review text ÷ evidenced areas | ↑ |
| `surface.review.response_rate` | Responses ÷ reviews | ↑ |
| `surface.review.response_latency_median_hours` | | ↓ |
| `surface.freshness.post_cadence_7d` | Posts per week, trailing 8 weeks | ↑ |
| `surface.freshness.photo_cadence_7d` | Photos per week, trailing 8 weeks | ↑ |
| `surface.freshness.days_since_last_activity` | | ↓ |
| `surface.organic.discovery_click_share` | Non-branded clicks ÷ total clicks | ↑ |
| `surface.organic.position_distribution` | Share of impressions in bands 1–3 / 4–10 / 11–20 / 20+ | ↑ |
| `surface.organic.gap_count` | Competitor-held queries client is absent from, post-filter | ↓ |
| `surface.serp.ai_answer_incidence` | Target queries showing an AI answer | context |
| `surface.site.thin_page_count` | Pages failing the differentiation test | ↓ |
| `surface.site.differentiation_index` | Mean pairwise dissimilarity across service×city pages | ↑ |

### Protocol layer
| Key | Definition | Direction |
|---|---|---|
| `protocol.schema.type_coverage` | Required types present ÷ required by page type | ↑ |
| `protocol.schema.validity_rate` | Valid blocks ÷ total | ↑ |
| `protocol.schema.content_match_rate` | Markup values matching visible content | ↑ |
| `protocol.identity.sameas_count` | Distinct verified `sameAs` targets | ↑ |
| `protocol.access.retriever_allowed` | Retrieval crawlers permitted (boolean per crawler) | ↑ |
| `protocol.feed.freshness_hours` | Age of most recent feed update | ↓ |
| `protocol.journey.completion_depth` | 0–5 rung reached in the agent journey test | ↑ |
| `protocol.readiness.rung` | Feed/endpoint ladder position | ↑ |

### Generative layer
| Key | Definition | Direction |
|---|---|---|
| `geo.mention_rate` | Probes mentioning client ÷ probes run | ↑ |
| `geo.shortlist_rate` | Probes placing client in shortlist | ↑ |
| `geo.primary_rate` | Probes returning client as sole/first recommendation | ↑ |
| `geo.citation_rate` | Probes citing a client-owned URL | ↑ |
| `geo.third_party_grounding_share` | Client-supporting citations from non-owned sources ÷ all client-supporting citations | ↑ |
| `geo.share_of_answer` | Client mentions ÷ all provider mentions across probe set | ↑ |
| `geo.factual_error_rate` | Probes containing a false statement about the client | ↓ |
| `geo.probe_variance` | Std dev of mention across repetitions | context |

### Outcome layer
`outcome.enquiry_count` · `outcome.qualified_rate` · `outcome.booked_jobs` · `outcome.revenue` · `outcome.cost_per_qualified_enquiry` · `outcome.attributed_share`

Every engagement must land here. Visibility metrics that never connect to enquiries are how agencies lose accounts they were technically succeeding at.

---

## 2. Scoring model

**Gap size** — normalise everything to a 0–1 deficit against the peer set:
`gap = clamp((peer_p75 − client_value) ÷ max(peer_p75, ε), 0, 1)` for ↑ metrics; inverted for ↓ metrics.

Use **p75, not the median**, as the target. Parity with the median makes you eligible; p75 makes you chosen. State this to the client — it reframes the goal from "catch up" to "be the obvious answer".

**Priority score**
`priority = (impact_weight × gap × confidence) ÷ (effort_weight × latency_weight)`

- `impact_weight` from `EffectEstimate` where confidence grade is A/B; otherwise from the default table below, marked `hypothesis`.
- `confidence` from observation confidence and sample adequacy.
- `latency_weight`: 0–7d = 1.0 · 7–30d = 1.3 · 30–90d = 1.8 · 90d+ = 2.5.

**Default impact weights** (use until you have your own effect estimates — then replace, and record the replacement date):

| Action type | Default weight | Basis |
|---|---|---|
| Fix entity inconsistency / duplicate | 1.0 | Strong practitioner consensus, foundational |
| Correct primary category | 1.0 | Strongest consistently observed lever |
| Add parity secondary categories | 0.8 | Widely observed, fast |
| Claim unclaimed profiles | 0.8 | Foundational |
| Add filter attributes | 0.6 | Direct eligibility effect under refinements |
| Complete services + descriptions | 0.5 | Moderate |
| Increase review velocity | 0.7 | Strong on both ranking and conversion |
| Deploy/repair schema + `sameAs` | 0.6 | Rising; foundational for GEO |
| Title/meta on position 11–20 pages | 0.7 | Fast, measurable |
| Build evidenced service×city page | 0.6 | Slow but durable |
| Post/photo cadence | 0.4 | Real but modest and contested |
| Review responses | 0.4 | Strong on conversion, contested on ranking |
| Publish feeds / availability | 0.3 now, rising | Optionality play — state it as such |

Honesty rule: these are **priors**, not findings. Show the client which are which.

---

## 3. Contested claims register

Maintain this. It is what separates a credible practice from the content-mill version, and it is directly useful in sales conversations with sophisticated buyers.

| Claim | Status | How to handle |
|---|---|---|
| "Photos drive 42% more direction requests / 35% more clicks" | Vendor marketing figure, old, uncontrolled | Do not use as a projection. Justify photos on evidence and conversion grounds |
| "Responding to reviews improves ranking" | Plausible, weakly evidenced as a direct ranking factor | Label `hypothesis`; justify on conversion and evidence density |
| "Posting weekly improves ranking" | Mixed evidence; freshness effects are real but modest and inconsistent | Label `hypothesis`; justify on engagement and content supply |
| "Keyword-stuffed business name ranks better" | Observably effective and against policy | **Never recommend.** Report competitors doing it as a policy-violation option for the client to report |
| "More categories is always better" | False — irrelevant categories dilute and risk suspension | Eligibility test on every category |
| "Reviews mentioning keywords rank you for them" | Directionally supported, effect size unclear | Recommend natural guidance, never scripts |
| "Proximity can be beaten by optimisation" | Partially — proximity dominates but is not absolute | Set realistic geographic expectations at onboarding, in writing |
| "AI Overviews destroy all organic traffic" | Overstated; effect varies hugely by intent class | Measure per client with `surface.serp.ai_answer_incidence` |
| "`llms.txt` improves AI visibility" | Unproven; adoption unsettled | Cheap optionality, framed as such |
| "You can submit a business to an AI engine" | False | Correct the client directly |

Review quarterly. Move claims between statuses as your own `EffectEstimate` data accumulates — that migration, from folklore to measured, is the core intellectual product of the practice.

---

## 4. Benchmark construction rules

1. **Cell definition:** `sector_code × market × size_band × metric_key`. Never benchmark across sectors — a dental practice and an emergency plumber have incomparable review velocities.
2. **Minimum n:** suppress cells with fewer than 5 clients or 20 observations. Suppress, never approximate.
3. **Anonymise at write.** Aggregates are computed on ingest; the benchmark store holds no client identifiers and no client-level rows. This is what makes it safe to use across a client base.
4. **Recency window:** default 90 days. Longer for slow metrics (`entity.*`), shorter for volatile ones (`geo.*`, pack position).
5. **Outlier handling:** winsorise at p5/p95; report both raw and winsorised n.
6. **Contribution is opt-in** and recorded in `Client.consent_scope`. A client who does not contribute may still receive benchmarks if their contract says so — but be explicit about the asymmetry in the contract.
7. **Two-sided value:** the client sees their percentile position, never another client's identity or values.

---

## 5. Effect estimation rules

The hardest and most valuable part. Discipline here is the difference between a learning system and a superstition engine.

1. **Clean event definition:** no other change shipped on the same surface within ±7 days; no known platform-wide event in the window; baseline of ≥14 days pre.
2. **Window:** pre-14d mean vs. post-30d mean, with the first 3 days post-change excluded (propagation lag).
3. **Control:** where possible, compare against the same metric in the same sector×market cell over the same window, to net out platform-level movement. This portfolio control is the main methodological advantage of multi-tenancy — a single-client operator simply cannot do it.
4. **Minimum n:** report no effect estimate below 10 clean events; grade A only at ≥30.
5. **Confidence grades:** A ≥30 clean, portfolio-controlled, consistent direction · B ≥15, controlled, mostly consistent · C ≥10, uncontrolled · D anecdotal — do not use in scoring.
6. **Publish negatives.** Actions that show no effect are as valuable as those that do, because they let you stop selling them. This is the single most commercially useful discipline in the whole system and the one most agencies refuse to adopt.
7. **Never report a causal claim from a single client.**

---

## 6. Reporting standards

- Every metric shown with `observed_at` and, where volatile, n and variance.
- Every performance chart annotated with `ChangeEvent` markers. Unannotated time series are unreadable and invite false attribution.
- Position metrics always paired with presence metrics.
- Discovery/branded split shown on every organic chart.
- Benchmark position shown as a percentile band, not a competitor name.
- Every report opens with: what changed, what moved, what we learned, what's next. In that order.
