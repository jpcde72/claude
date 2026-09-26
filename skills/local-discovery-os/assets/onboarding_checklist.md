# LDOS Onboarding Checklist (Phase 0–1)

Two weeks. Nothing ships until every gate is passed.

## Week 1 — Govern and canonicalise

**Governance**
- [ ] Tenant and client records created; `tenant_id` assigned
- [ ] `sector_code` and `market` set from the fixed taxonomy (benchmark join keys — get these right or the client contributes nothing and receives nothing)
- [ ] Consent scope captured in writing: properties, publishing authority, benchmark contribution, competitor naming, case study, retention
- [ ] Conflict check run against existing client base for this market
- [ ] Credential handles registered via delegated access; no shared logins
- [ ] Ethical perimeter and non-claims shared with client and acknowledged
- [ ] Measurement baseline date fixed; reporting cadence agreed

**Canonical record**
- [ ] Single true name / address / phone / hours agreed and locked
- [ ] Service catalogue captured with `price_basis`, `margin_rank`, `demand_rank`
- [ ] Service areas declared with `is_evidenced` set honestly for each
- [ ] Credentials captured with issuer verification URLs
- [ ] `is_service_area_business` set explicitly, not inferred
- [ ] Record validated against `client_entity.schema.json`
- [ ] `canonical_locked_at` stamped

## Week 2 — Observe and baseline

**Entity resolution (W1)**
- [ ] Surface sweep complete across profile, registry, directory and review platforms
- [ ] Variance register produced; every inconsistency classified
- [ ] Duplicate search run by phone, address and former name
- [ ] `entity.consistency.nap_variance` computed

**Competitive and market baseline**
- [ ] 8–15 target queries defined across intent classes
- [ ] Pack observed from ≥3 grid points per priority area
- [ ] SERP shape recorded per query (AI answer present? pack present? marketplace dominant?)
- [ ] Competitor set built, including aggregators and marketplaces
- [ ] Full observation run: W2–W11, single day where possible

**Protocol and generative baseline**
- [ ] Crawler and agent access policy audited — **do this first, it can invalidate everything downstream**
- [ ] Schema inventory and validation run
- [ ] Agent journey test run to failure point; `protocol.journey.completion_depth` recorded
- [ ] Probe set instantiated from `probe_set.template.json` with client variables
- [ ] Probe baseline run: 3 repetitions, full set, variance recorded
- [ ] Agent Readiness Index scored with all five components

**Diagnosis and plan**
- [ ] Benchmark join complete; gaps scored against sector p75
- [ ] Every gap carries a `lost_query_example`
- [ ] Every recommendation carries `evidence_refs` and honest `impact_basis`
- [ ] Backlog ranked by priority score
- [ ] 90-day plan sequenced: entity → eligibility → justification → defaults → protocol

## Kickoff deliverable

Five things, in this order:
1. Where you are now — Agent Readiness Index with components, benchmark percentiles
2. What is broken at the foundation — variance register and eligibility gaps
3. What we will ship in 90 days — the sequenced backlog with latency bands
4. How we will know it worked — change log method, metric spine, verification
5. What we cannot promise — the non-claims list, in writing

## Hard gates

- No execution before the canonical record is locked.
- No page build before evidenced coverage is confirmed.
- No probe reporting from a single run.
- No recommendation without evidence and an honest impact basis.
