# LDOS Ontology

The shared data model for every client, every audit, and the cross-client benchmark base.

## Contents
1. Design principles
2. Entity map
3. Core entities (identity)
4. Observation entities (evidence)
5. Judgement entities (diagnosis and action)
6. Learning entities (benchmarks)
7. Relationship table
8. Field-level provenance and refresh
9. Identifier conventions
10. Extension rules

---

## 1. Design principles

**Separate the four kinds of thing.** Most SEO tooling collapses them, which is why insight doesn't compound.

| Kind | Nature | Mutability | Example |
|---|---|---|---|
| **Identity** | What is true about the client and its market | Slow-changing, human-asserted, verifiable | `Service`, `ServiceArea`, `Competitor` |
| **Evidence** | What was seen, where, when, by what method | Immutable once written; append-only | `Observation`, `ProbeResult` |
| **Judgement** | What we concluded and decided to do | Versioned, attributable to a person or model | `Gap`, `Recommendation`, `Task` |
| **Learning** | What generalises across clients | Aggregated, anonymised, statistical | `Benchmark`, `EffectEstimate` |

Consequences:
- Evidence is never overwritten. A changed value is a **new observation**, and the diff is the product.
- Judgement always cites evidence. A recommendation without an `evidence_ref` is invalid.
- Learning never contains client-identifying rows. Aggregation happens at write time, not at read time.

**Everything is dual-keyed** by `tenant_id` and entity id. There is no un-scoped read path.

---

## 2. Entity map

```
Tenant
 └── Client
      ├── Location (1..n)
      │    ├── EntityProfile (1 per Surface)   ← the client's rendering on GBP, Bing, Apple, Yelp…
      │    ├── ServiceArea (1..n)              ← polygon / named area / radius
      │    └── Capacity                        ← hours, staff, emergency cover, lead time
      ├── Service (1..n) ──< ServiceVariant
      ├── Category (primary + secondary)
      ├── Attribute (1..n)
      ├── Credential (licence, insurance, certification, membership)
      ├── Competitor (1..n) ──> Location ──> EntityProfile
      ├── KeywordTarget (1..n) ──> Query
      ├── WebPage (1..n)
      └── AgentInterface (0..n)                ← feed, booking endpoint, MCP server, API

Surface (reference data, shared across tenants)
 └── SurfaceClass  (map / organic / answer-engine / directory / review / marketplace / agent)

Observation ──> (Location | EntityProfile | WebPage | Query | Competitor | Surface)
Probe ──> ProbeResult ──> Citation

Gap ──> Recommendation ──> Task ──> Artefact ──> ChangeEvent ──> MetricSeries
Benchmark <── (aggregated) ── Observation + ChangeEvent + MetricSeries
```

---

## 3. Core entities (identity)

### Tenant
`tenant_id` (pk) · `name` · `region` · `data_residency` · `benchmark_contribution` (none | aggregated | full) · `retention_days` · `created_at`

### Client
`client_id` (pk) · `tenant_id` · `legal_name` · `trading_name` · `sector_code` (fixed taxonomy — required for benchmarking) · `market` (ISO country + region) · `size_band` (solo / 2–10 / 11–50 / 50+) · `founded_date` · `avg_job_value` · `avg_job_value_currency` · `lead_time_days` · `engagement_tier` · `consent_scope[]` · `status`

`sector_code` and `market` are the join keys for every benchmark. Get them right at intake or the client contributes nothing and receives nothing.

### Location
`location_id` (pk) · `client_id` · `label` · `address_line[]` · `locality` · `region` · `postcode` · `country` · `lat` · `lng` · `place_id` · `cid` · `phone_e164` · `is_service_area_business` · `storefront_visible` · `opened_date` · `status` (active / temporarily_closed / closed)

`is_service_area_business` changes almost every downstream rule (proximity weighting, address display, area declaration limits). Set it explicitly; never infer.

### EntityProfile
One per (Location × Surface). This is the client's *rendering*, distinct from the client's *truth*.

`profile_id` (pk) · `location_id` · `surface_id` · `profile_url` · `claimed` (bool) · `verified` (bool) · `verification_method` · `displayed_name` · `displayed_address` · `displayed_phone` · `displayed_hours` · `primary_category` · `secondary_categories[]` · `attributes[]` · `description_text` · `description_chars` · `services_listed[]` · `photo_count` · `review_count` · `rating_mean` · `last_observed_at` · `consistency_flags[]`

`consistency_flags` is the Entity Layer defect list: `name_variant`, `phone_variant`, `hours_conflict`, `category_conflict`, `duplicate_suspected`, `unclaimed`, `closed_flag_risk`.

### Service
`service_id` (pk) · `client_id` · `name` · `canonical_name` (mapped to a shared service taxonomy) · `description` · `price_band_low` · `price_band_high` · `price_basis` (fixed / hourly / from / quote-only) · `is_emergency` · `typical_duration_minutes` · `seasonality[]` · `margin_rank` · `demand_rank` · `is_primary`

`margin_rank` and `demand_rank` are what stop the service catalogue becoming an undifferentiated list. Optimise for high-margin × high-demand first, always.

### ServiceVariant
`variant_id` · `service_id` · `qualifier` (e.g. residential / commercial / same-day / specific make) · `distinct_query_demand` (bool)

Only promote a variant to its own page or GBP service if `distinct_query_demand` is true.

### ServiceArea
`area_id` (pk) · `location_id` · `type` (named_place / polygon / radius / postcode_set) · `geometry` (GeoJSON) · `named_place` · `admin_level` · `travel_time_minutes` · `is_declared_on_profile` (bool) · `is_evidenced` (bool) · `evidence_refs[]` · `priority_rank`

`is_evidenced` is the honesty check and the AXO differentiator: can you demonstrate delivered work, reviews, or physical presence in this area? Declaring areas you cannot evidence is the single most common cause of thin, non-ranking city pages — and increasingly of exclusion from agent shortlists, which weight corroborated coverage.

### Category
`category_id` · `client_id` · `surface_id` · `category_string` · `surface_native_id` · `role` (primary / secondary) · `held_by_competitor_count` · `status` (held / recommended / rejected) · `rationale`

### Attribute
`attribute_id` · `client_id` · `surface_id` · `attribute_key` · `attribute_label` · `value` · `is_self_declared` · `held_by_competitor_count` · `affects_eligibility` (bool) · `affects_justification` (bool)

Some attributes are filters (they gate whether you appear at all under a refinement) and some are trust signals (they change click and choice). Tag both; they justify different priorities.

### Credential
`credential_id` · `client_id` · `type` (licence / insurance / certification / membership / award) · `issuer` · `identifier` · `valid_from` · `valid_to` · `verification_url` · `is_machine_verifiable`

Under-used today, decisive tomorrow. Agents filtering on "licensed and insured" need something resolvable, not an adjective on a homepage.

### Competitor
`competitor_id` · `client_id` · `name` · `location_ids[]` · `profile_urls[]` · `website` · `competitor_type` (direct_local / franchise / national_aggregator / marketplace / platform_native) · `first_seen_at` · `share_of_pack` · `notes`

Include `national_aggregator` and `marketplace` explicitly. In many local categories the real competitor for an agent's attention is a lead-gen marketplace, not the firm down the road — and the counter-strategy is different (protocol-layer, not map-pack).

### KeywordTarget / Query
`query_id` · `query_string` · `intent_class` (emergency / research / comparison / transactional / navigational) · `modifier_flags[]` (near_me / city / best / cheap / open_now / brand) · `volume_estimate` · `volume_source` · `difficulty_estimate` · `serp_features[]` · `ai_answer_present` (bool) · `local_pack_present` (bool)

`ai_answer_present` and `serp_features` must be observed per market and re-observed; they change and they materially change the value of a #1 blue link.

### WebPage
`page_id` · `client_id` · `url` · `page_type` (home / service / service_city / city_hub / location / proof / faq / blog / legal) · `target_query_id` · `h1` · `title` · `meta_description` · `word_count` · `schema_types[]` · `internal_inlinks` · `internal_outlinks` · `last_modified` · `indexed` (bool) · `canonical_target`

### AgentInterface
`interface_id` · `client_id` · `type` (structured_data / product_feed / availability_feed / booking_api / quote_api / mcp_server / llms_txt / knowledge_endpoint) · `url` · `format` · `auth_required` · `update_frequency` · `last_validated_at` · `validation_status` · `agent_accessible` (bool)

---

## 4. Observation entities (evidence)

### Surface (shared reference data)
`surface_id` · `name` · `surface_class` (map / organic / answer_engine / directory / review / marketplace / agent) · `operator` · `market_coverage[]` · `is_llm_grounded` (bool) · `accepts_structured_feed` (bool)

Maintaining Surface as shared reference data — not per-client free text — is what allows "which surfaces matter in this sector and market?" to become a benchmark question.

### Observation
The atomic evidence record. Append-only.

`observation_id` (pk) · `tenant_id` · `subject_type` · `subject_id` · `surface_id` · `metric_key` · `value_numeric` · `value_text` · `value_json` · `unit` · `observed_at` · `method` (manual / browser_agent / api / tool_export / model_inference) · `location_context` (lat/lng or named locale used for the query) · `device_context` (mobile / desktop) · `language` · `confidence` (0–1) · `is_estimate` (bool) · `estimate_method` · `raw_snapshot_ref` · `operator_id`

Non-negotiable fields: `observed_at`, `method`, `location_context`, `confidence`. Local results vary by device, locale, personalisation, and time. An observation without context is not evidence.

`metric_key` comes from a controlled vocabulary (see `references/benchmarks.md`), never free text.

### Probe / ProbeResult / Citation
The GEO/AXO evidence path. Detailed in `references/geo-axo.md`.

- `Probe`: `probe_id` · `client_id` · `prompt_text` · `intent_class` · `engine` · `market` · `persona` · `run_frequency`
- `ProbeResult`: `result_id` · `probe_id` · `run_at` · `engine_version_hint` · `response_text_ref` · `client_mentioned` (bool) · `client_rank_in_answer` · `competitors_mentioned[]` · `answer_shape` (single / shortlist / refusal / clarifying_question)
- `Citation`: `citation_id` · `result_id` · `cited_url` · `cited_domain` · `is_client_owned` · `is_third_party_about_client` · `claim_supported`

`is_third_party_about_client` is the metric that matters most and the one nobody tracks: how often the model grounds a claim about the client in a source the client does not own.

### ChangeEvent
`change_id` · `client_id` · `task_id` · `layer` · `surface_id` · `field_changed` · `value_before` · `value_after` · `shipped_at` · `verified_at` · `verification_method` · `reversal_of`

The measurement spine. Without dated change events, all before/after analysis is storytelling.

### MetricSeries
`series_id` · `client_id` · `metric_key` · `granularity` (day / week / month) · `points[]` (`date`, `value`, `source`) · `baseline_value` · `baseline_date`

---

## 5. Judgement entities

### Gap
`gap_id` · `client_id` · `layer` (entity / surface / protocol) · `arena` (eligibility / justification / defaults) · `metric_key` · `client_value` · `peer_median` · `peer_p75` · `gap_size` · `gap_direction` · `structural_or_operational` · `confidence` · `evidence_refs[]` · `lost_query_examples[]`

`lost_query_examples` enforces the diagnosis rule: if you can't name what the gap loses, it isn't a gap.

### Recommendation
`recommendation_id` · `gap_ids[]` · `action_type` · `description` · `impact` (H/M/L) · `impact_basis` (benchmark / prior_effect_estimate / hypothesis) · `effort` · `latency_band` · `dependencies[]` · `risk_flags[]` · `verification_method` · `status`

`impact_basis` is the intellectual honesty field. Three quarters of local-SEO advice is `hypothesis` wearing the clothes of `benchmark`.

### Task
`task_id` · `recommendation_id` · `client_id` · `owner` · `automation_class` (automate / assist / retain) · `due_at` · `blocked_by[]` · `state` · `output_artefact_ids[]`

### Artefact
`artefact_id` · `task_id` · `type` (description / post / photo_brief / review_response / page_spec / page_copy / schema_block / feed_file / report) · `content_ref` · `target_surface_id` · `generated_by` (model / human / hybrid) · `approved_by` · `approved_at` · `published_at` · `published_url`

`generated_by` and `approved_by` are the audit trail you will need the first time a client asks who wrote something, or a platform asks about disclosure.

---

## 6. Learning entities

### Benchmark
`benchmark_id` · `sector_code` · `market` · `size_band` · `metric_key` · `n_clients` · `n_observations` · `p25` · `p50` · `p75` · `p90` · `computed_at` · `window_days` · `min_n_satisfied` (bool)

Never publish or use a benchmark cell with `n_clients < 5`. Suppress, don't approximate.

### EffectEstimate
`effect_id` · `sector_code` · `action_type` · `metric_key` · `n_change_events` · `median_effect` · `iqr` · `median_latency_days` · `confounder_notes` · `confidence_grade` (A/B/C/D)

This is the crown jewel and the hardest to earn. It is the answer to "if we add these three categories, what actually happens?" — derived from your own change events across clients, not from folklore. Grade honestly: A requires ≥30 clean change events with no co-shipped confounders.

---

## 7. Relationship table

| From | Relation | To | Cardinality | Notes |
|---|---|---|---|---|
| Client | operates | Location | 1..n | multi-location changes nearly every rule |
| Location | renders_as | EntityProfile | 1..n | one per surface |
| Location | covers | ServiceArea | 1..n | declared vs evidenced tracked separately |
| Client | offers | Service | 1..n | |
| Service | targets | Query | n..n | via KeywordTarget |
| Query | resolves_on | Surface | n..n | with SERP feature flags |
| Client | competes_with | Competitor | 1..n | per query, per surface — competitor sets differ by query |
| Observation | describes | any subject | n..1 | append-only |
| Gap | evidenced_by | Observation | n..n | |
| Recommendation | addresses | Gap | n..n | |
| Task | implements | Recommendation | 1..1 | |
| ChangeEvent | results_from | Task | 1..1 | |
| MetricSeries | measures_effect_of | ChangeEvent | n..n | time-window join |
| Benchmark | aggregates | Observation | n..n | anonymised at write |
| EffectEstimate | aggregates | ChangeEvent + MetricSeries | n..n | anonymised at write |

**The two joins that create the business:** `ChangeEvent → MetricSeries` (did it work for this client?) and `EffectEstimate ← ChangeEvent across clients` (does it work generally?). Everything else is table stakes.

---

## 8. Field-level provenance and refresh

| Data group | Source | Method | Refresh | Decay risk |
|---|---|---|---|---|
| Client identity, credentials | Client, registry | Human + verification | On change; annual re-verify | Low |
| Categories, attributes | Surface UI | Browser agent | Monthly; on platform change | **High** — taxonomies change without notice |
| Profile description, services | Surface UI | Browser agent | Quarterly | Medium |
| Photos, posts | Surface UI | Browser agent | Weekly | Medium |
| Reviews, velocity | Surface UI / API | API preferred | Weekly | Medium |
| Rankings, pack composition | Localised query | Browser agent, gridded | Weekly, fixed grid | **Very high** — volatile, personalised |
| Search Console metrics | Property API | API | Daily pull, weekly read | Low |
| Website structure, schema | Crawl | Crawler + validator | Weekly | Medium |
| AI answer probes | Assistant APIs/UIs | Probe runner | Weekly, fixed prompt set | **Very high** — non-deterministic |
| Competitor set | Pack observation | Derived | Monthly | High |
| Benchmarks | Internal aggregate | Batch | Monthly | Low |

Rule: anything marked high or very high decay must carry `observed_at` prominently in any client-facing output, and must never be presented as a stable fact.

---

## 9. Identifier conventions

- All ids: `{prefix}_{ULID}` — sortable by creation time, no collisions across tenants. `cli_`, `loc_`, `prf_`, `svc_`, `obs_`, `gap_`, `rec_`, `tsk_`, `chg_`, `prb_`.
- `metric_key`: `{layer}.{surface_class}.{concept}.{qualifier}` — e.g. `surface.map.review_velocity.30d`, `protocol.agent.schema_validity.localbusiness`, `entity.consistency.nap_variance`.
- `action_type`: verb-noun, controlled — `add_category`, `add_attribute`, `rewrite_description`, `publish_post`, `upload_photo_batch`, `respond_review`, `create_service_city_page`, `rewrite_title`, `add_internal_links`, `deploy_schema`, `publish_availability_feed`, `expose_booking_endpoint`.
- Timestamps: UTC ISO-8601 with explicit offset. Local time only in rendered output.

---

## 10. Extension rules

Extend the ontology when a new **surface class**, **decision arena input**, or **agent interface type** appears. Do not extend it for a one-off client request.

Process: propose field → declare which layer and arena it serves → declare refresh and decay → declare whether it is benchmarkable → version the schema (`schema_version` on every record) → backfill or mark null-eligible.

Deprecate rather than delete. Historical observations must remain interpretable under the schema version they were written against.
