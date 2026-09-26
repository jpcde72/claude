# Automation, Flows and Maintenance

How LDOS runs as a service rather than a series of projects.

---

## 1. The automation classification

Every task carries `automation_class`:

| Class | Definition | Test |
|---|---|---|
| **Automate** | Deterministic, high-frequency, low-judgement, low-blast-radius if wrong | Would you be comfortable if this ran unattended 500 times? |
| **Assist** | Model drafts, human approves before anything is published or shipped | Does a wrong output reach a client, a customer, or a public surface? |
| **Retain** | Judgement-dense, relationship-bearing, risk-bearing, or strategically consequential | Does getting this wrong cost trust, money, or legal exposure? |

**Default classification**

| Activity | Class | Note |
|---|---|---|
| Surface sweeps, profile extraction | Automate | |
| Pack observation on a fixed grid | Automate | |
| Review extraction and theming | Automate | |
| Schema crawl and validation | Automate | |
| Search Console / analytics ingestion | Automate | |
| Probe running and result parsing | Automate | |
| Benchmark computation | Automate | |
| Drift and anomaly detection | Automate | |
| Report assembly | Automate | Narrative section stays Assist |
| Copy generation (posts, descriptions, pages) | Assist | |
| Review response drafting | Assist | Never auto-publish |
| Gap classification and scoring | Assist | |
| Category and attribute change decisions | Retain | Eligibility and suspension risk |
| Service-area declaration | Retain | Honesty and quality risk |
| Coverage-page build/no-build decision | Retain | Quality gate |
| Review acquisition design | Retain | Policy and ethics |
| Access/crawler policy decision | Retain | Commercial and legal |
| Client narrative and prioritisation | Retain | |
| Anything touching a complaint, safety, or legal matter | Retain | Escalate |

**Re-classify quarterly.** The frontier moves in one direction: work migrates from Retain → Assist → Automate. The correct response is to move it, not to defend the human step for its own sake — and to notice that the *classification decision itself*, the governance layer, is what stays with you. The value migrates from doing the task to owning the policy, the ontology, and the evidence base.

---

## 2. The four flows

### Flow A — Onboarding (once per client, ~2 weeks)

```
Contract signed
 → create Tenant/Client/Location records, assign tenant_id
 → consent + benchmark-contribution capture
 → credential handle registration (never values)
 → canonical entity lock (W1.1)
 → surface sweep + variance register (W1.2–1.6)
 → competitor set discovery (pack observation, 3+ points × 8–15 queries)
 → baseline observation run: ALL workstreams, single day where possible
 → Agent Readiness Index baseline (geo-axo §6)
 → probe baseline (3 reps × full probe set)
 → benchmark join → gap set → ranked backlog
 → kickoff: baseline, backlog, 90-day plan, explicit non-claims
```

Gate: no execution begins until the canonical record is locked and the variance register exists.

### Flow B — Execution sprint (fortnightly)

```
Pull top-n backlog items by (impact × confidence) ÷ effort, respecting dependencies
 → generate artefacts (Assist)
 → human approval → publish
 → write ChangeEvent (dated, field-level, with value_before/value_after)
 → schedule verification observation at t+7 and t+30
 → verification: did the change actually land and persist?
 → feed outcome to MetricSeries and EffectEstimate
```

Two rules that make this work: **one meaningful variable per surface per fortnight** where possible, and **verify that changes persisted** — platforms silently revert edits, and unverified changes corrupt every downstream effect estimate.

### Flow C — Monitoring (continuous)

```
Daily:    GSC/analytics ingest · uptime and access checks
Weekly:   pack grid observation · review pull · post/photo cadence check
          · schema validation · priority probe run
Monthly:  full profile extraction · full probe set · competitor set refresh
          · benchmark recompute · Agent Readiness re-score
Quarterly: category taxonomy refresh · automation re-classification
          · probe set review · ontology change review
Annually: credential re-verification · index weight re-tune · consent refresh
```

### Flow D — Learning (monthly batch)

```
Collect ChangeEvents closed ≥30 days ago
 → filter to clean events (no co-shipped confounder on the same surface within ±7d)
 → join to MetricSeries windows (pre-14d baseline vs post-30d)
 → compute per-action effect distribution by sector × market × size_band
 → update EffectEstimate with n, median, IQR, confidence grade
 → suppress any cell with n < 5
 → publish updated impact_basis values back into the recommendation engine
```

Flow D is the compounding asset. Everything else is deliverable production; this is what makes year three cheaper and sharper than year one, and what a competitor cannot buy.

---

## 3. Trigger library

Event-driven work, not just scheduled.

| Trigger | Detection | Response | Priority |
|---|---|---|---|
| Profile edit reverted or overwritten | Weekly diff vs. last known state | Re-apply, log, investigate source | P1 |
| New competitor enters pack | Pack observation diff | Profile them; refresh competitor set | P2 |
| Competitor category or attribute change | Monthly extraction diff | Eligibility review | P2 |
| Negative review posted | Review pull | Response SLA clock starts (24h) | P1 |
| Review velocity drops below target 2 weeks running | Metric threshold | Acquisition process review with client | P2 |
| Rating drops >0.2 in 30 days | Metric threshold | Root-cause with client — likely operational, not marketing | P1 |
| Search Console impressions fall >25% w/w | Anomaly detection | Distinguish algorithmic, seasonal, technical, SERP-shape | P1 |
| Schema validation failure | Weekly crawl | Fix; check whether a site deploy caused it | P1 |
| Retriever access blocked | Access check | Escalate to whoever owns WAF/CDN config | P1 |
| Probe factual error about client | Probe parse | Trace to source, remediate, re-probe | P2 |
| `geo.share_of_answer` falls >20% month on month | Metric threshold | Check for engine change before assuming client cause | P2 |
| Availability feed stale >48h | Freshness check | Suppress the feed rather than serve stale data | P1 |
| Platform taxonomy change | Quarterly refresh or industry alert | Re-map categories across all clients | P1 (portfolio-wide) |
| Client closes/opens a location or service | Client notification | Full entity propagation across all surfaces | P1 |

Portfolio-wide triggers (taxonomy changes, engine changes) are where multi-client scale pays: you detect once and remediate across every client. Build the detection to run at portfolio level, not per client.

---

## 4. Drift detection

Three kinds of drift, each needing a different response.

**Data drift** — an observation source changes shape (a platform redesigns, an export column moves, a selector breaks). Detect via schema validation on ingest and a completeness check per run. Response: fix the collector; **mark the affected window as low-confidence rather than deleting it**, and exclude it from benchmarks.

**Entity drift** — the client's reality diverges from the record (new service, new area, price change, staff change). Detect via quarterly client confirmation plus contradiction checks between website, profile, and record. Response: re-canonicalise and propagate. This is the most common cause of embarrassing client-facing errors.

**Model drift** — the answer engines change behaviour. Detect via probe variance step-changes and citation-pattern shifts across the whole client portfolio simultaneously. Response: if it moves across all clients at once, it is a platform event; report it as such and do not let it be read as client performance. **This portfolio-level detection is only possible with multi-tenant data, and it is a genuine analytical advantage over any single-client operator.**

---

## 5. Cadence commitments (what the client actually buys)

| Cadence | Deliverable |
|---|---|
| Weekly | Cadence execution (posts, photos, review responses), monitoring, exception alerts |
| Fortnightly | Execution sprint: backlog items shipped, change log |
| Monthly | Performance read against change events; Agent Readiness re-score; probe report with variance; next-sprint backlog |
| Quarterly | Strategic review: benchmark position vs. sector peers, effect-estimate updates, roadmap re-plan, automation re-classification |
| Annual | Full re-audit, entity re-verification, index re-weighting |

Sell the cadence and the change log, not report volume. The single most persuasive artefact is a dated list of what changed and what moved.

---

## 6. Quality gates

Ship-blockers. Each is a hard stop, not a preference.

1. **Truth gate** — every claim in an artefact traces to the entity record.
2. **Evidence gate** — every recommendation carries `evidence_refs` and an honest `impact_basis`.
3. **Differentiation gate** — no page ships that fails the place-name-strip test (W11.4).
4. **Policy gate** — no review gating, no incentivised reviews, no fabricated attributes, no unevidenced service areas, no cloaking, no auto-published review responses.
5. **Attribution gate** — no change ships without a `ChangeEvent`.
6. **Verification gate** — no change closes without a t+7 persistence check.
7. **Freshness gate** — no feed or availability signal is published unless it is genuinely maintained.
8. **Claim gate** — no ranking or AI-inclusion guarantee appears in any artefact, internal or external.

---

## 7. Failure recovery

| Failure | Immediate action | Structural fix |
|---|---|---|
| Profile suspended | Read the actual policy cited; do not resubmit blind; reinstatement request with evidence | Pre-change policy review on all Retain-class edits |
| Rankings drop after a shipped change | Check change log first, then platform-wide signal, then technical | One-variable-per-sprint discipline |
| Model states something false and damaging | Trace grounding source; remediate at source; re-probe; document | Third-party corroboration programme (W5) |
| Client-reported lead drop with stable metrics | Check call tracking, form health, spam filtering, and answer rate before touching SEO | Lead-path monitoring in Flow C |
| Benchmark cell moves sharply | Check for a single client dominating the cell | Minimum-n and outlier rules in Flow D |
| Collector silently returns empty | Completeness check on ingest | Alert on zero-row runs; never treat empty as zero |
