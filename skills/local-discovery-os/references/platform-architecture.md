# Platform Architecture (forward spec)

The build target that the skill and ontology are designed to feed. Nothing here is required to *run* LDOS manually — it is required to run it for thirty clients without the quality degrading.

---

## 1. Design constraints

1. **The ontology is the contract.** Storage, API, and UI all derive from `ontology.md`. Any field the UI shows must exist in the schema first.
2. **Append-only evidence, versioned judgement.** Observations never mutate. Recommendations and artefacts version.
3. **Tenant isolation at the data layer**, not the app layer.
4. **The agent is a first-class client of the API**, not a bolt-on. Every collector and generator authenticates as a service identity with a scoped role.
5. **Aggregation on write.** Benchmark tables never require a cross-tenant read at query time.
6. **Every number in the UI is clickable through to its observation.** If a figure can't be traced, it doesn't render.

---

## 2. Storage layout

| Store | Holds | Why |
|---|---|---|
| **Relational (Postgres)** | Identity, judgement, change log, tasks, artefacts metadata | Relational integrity, row-level security by `tenant_id` |
| **Time-series / columnar** | `Observation`, `MetricSeries`, `ProbeResult` | High-volume append, window queries |
| **Object store** | Raw snapshots (HTML, JSON, screenshots, response text) | Cheap, immutable, referenced by `raw_snapshot_ref` |
| **Vector index** | Review text, probe responses, competitor copy, page content | Thematic clustering, similarity, differentiation index |
| **Aggregate store** | `Benchmark`, `EffectEstimate` | Written by the aggregation job only; no tenant columns |
| **Secrets manager** | Credential values | Never in the primary DB |

Row-level security policies on every tenant-scoped table. The aggregation job is the only identity permitted to bypass them, and its output schema physically cannot hold a tenant identifier.

---

## 3. Services

| Service | Responsibility | Class |
|---|---|---|
| **Intake** | Client/location/service onboarding, canonical record lock, validation against schema | Assist |
| **Collector fleet** | Surface sweeps, pack grids, review pulls, schema crawls, GSC/analytics ingest. One collector per source, each emitting `Observation` records with mandatory context fields | Automate |
| **Probe runner** | Fixed probe set × engines × repetitions; parses mentions, citations, answer shape | Automate |
| **Validator** | Schema validity, content-match, access checks, feed freshness, completeness checks on every collector run | Automate |
| **Diagnostician** | Benchmark join, gap computation, scoring | Assist |
| **Generator** | Artefact production against production rules | Assist |
| **Workflow** | Backlog, sprints, approvals, SLAs, change log, verification scheduling | Automate |
| **Aggregator** | Monthly benchmark and effect-estimate batch, with n-suppression | Automate |
| **Alerting** | Trigger library from `automation.md` | Automate |
| **Reporting** | Report assembly with change-event annotation | Automate (narrative Assist) |

Collectors are the fragile part. Build them with: a completeness assertion per run, a schema check on output, automatic low-confidence marking on partial runs, and a zero-row alarm. **Never let an empty collector run be recorded as a zero value** — that single defect will silently corrupt every benchmark you build.

---

## 4. Front end

Five surfaces. Resist adding a sixth.

**1. Portfolio view** (agency operator)
Client grid: Agent Readiness Index, open P1 triggers, sprint status, benchmark percentile, contract health. Sorted by attention needed, not alphabetically. Portfolio-wide anomaly banner when a metric moves across many clients at once — that's the platform-event signal from `automation.md` §4.

**2. Client workspace**
Tabs: Entity · Surface · Protocol · Backlog · Change log · Reports. Each metric renders with `observed_at`, confidence, and a link to the underlying observation. The change log is the spine — a dated, filterable list of every shipped change with its verification state and its measured effect.

**3. Audit runner**
Trigger a workstream, watch collectors execute, review outputs, promote observations into gaps. Human-in-the-loop review queue for anything the diagnostician scored with low confidence.

**4. Artefact studio**
Generate, edit, approve, publish. Diff view against what is currently live. Approval gate enforced in the workflow, not by convention. Every artefact stamped with `generated_by` / `approved_by`.

**5. Benchmark explorer**
Percentile position by metric, sector, market, size band, with n and suppression state visible. Effect-estimate browser with confidence grades — including the negative results, which is the view that will change how the practice sells.

**Client-facing portal** (separate, read-only): Agent Readiness Index and components, change log, performance against change events, percentile bands, next sprint. Nothing else. Client portals fail by showing everything.

---

## 5. Agent integration

The platform should be operable by an agent as well as by a person:

- **MCP server over the platform API** exposing scoped tools: `get_client_context`, `run_workstream`, `write_observation`, `score_gaps`, `draft_artefact`, `submit_for_approval`, `log_change_event`, `query_benchmark`.
- Scoped service identities: collectors get write-observation only; generators get draft-only; nothing gets publish without passing through the approval gate.
- The skill in this package is the operating manual for that agent. Keep them versioned together — a skill that drifts from the API it drives is worse than no skill.

---

## 6. Build sequence

Do not build this in order of interest. Build it in order of what stops working first as client count grows.

| Phase | Build | Unlocks |
|---|---|---|
| **1** | Schema + Postgres + tenancy + intake + change log | Multi-client without spreadsheet chaos. **The change log first** — it is retroactively impossible to reconstruct |
| **2** | Collector fleet for GBP, reviews, pack grid, GSC + observation store | Repeatable audits; the evidence base starts accruing from day one |
| **3** | Diagnostician + backlog + approval workflow | The service becomes consistent between operators |
| **4** | Probe runner + Agent Readiness Index | The GEO/AXO differentiator becomes measurable and sellable |
| **5** | Aggregator + benchmark explorer | Cross-client learning; pricing power |
| **6** | Artefact studio + client portal | Margin and retention |
| **7** | MCP server + agent operation | Scale without linear headcount |

Phases 1 and 2 have a property worth noticing: they produce a compounding data asset from the first client, before any of the clever parts exist. Every month they are delayed is a month of evidence that cannot be recovered.

---

## 7. Open questions to resolve before building

1. **Collector strategy** — browser automation, third-party APIs, or a hybrid? Trades cost, fragility, and terms-of-service exposure. Decide per source and document the rationale.
2. **Probe engine access** — API access where available gives determinism and logging; UI access reflects what users actually see. They diverge. Probably both, tagged separately.
3. **Multi-location modelling** — a 40-branch franchise and 40 single-site clients are structurally different. Decide whether `Location` or `Client` is the primary billing and benchmarking unit before the schema hardens.
4. **Benchmark contribution as pricing lever** — contributing clients get benchmark access at a lower tier? Attractive, but creates an incentive to contribute low-quality data. Needs a quality gate if adopted.
5. **Conflict policy** — two competing clients in one market. Decide the firm's position now, not when the second one signs.
6. **Where the effect-estimate work lives** — this is research, not delivery. If it is funded out of delivery capacity it will never happen, and it is the entire long-term moat.
