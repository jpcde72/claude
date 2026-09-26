# Governance

Consent, tenancy, credentials, and the ethical perimeter. Read at Phase 0 for every new client.

---

## 1. Consent scope

Capture explicitly at onboarding, in writing, per item:

| Scope item | Options | Default |
|---|---|---|
| Property access | Which GBP locations, GSC properties, analytics views, rank-tool projects | Named list only, no blanket access |
| Publishing authority | Draft-only / publish-with-approval / publish-autonomous per surface | Publish-with-approval |
| Benchmark contribution | none / aggregated / full | **aggregated** |
| Competitor naming | May we name this client as a competitor in another client's report? | **No** |
| Case study use | Named / anonymised / none | Anonymised |
| Retention | Observation and change-log retention period | 36 months |
| Crawler and agent access policy | Who decides; what the default is | Client decides, we recommend |

The competitor-naming rule matters more than it looks. Serving two competing businesses in one market is a live conflict; either decline, or operate a documented separation with the informed consent of both. Decide the firm's policy once, and write it into the standard contract.

---

## 2. Tenancy and isolation

- `tenant_id` is on **every** record and enforced at the query layer, not the application layer. No un-scoped read path exists.
- Cross-tenant reads are permitted only through the benchmark aggregation job, which runs with a dedicated service identity, writes only aggregates, and is logged.
- Benchmark output contains no client identifiers, no free-text fields, and no cell below minimum n.
- Per-tenant encryption keys where the platform supports it; per-tenant export and deletion must be a single operation.
- Deletion means deletion: raw observations, snapshots, artefacts, and credentials. Aggregates already written are non-reversible and this must be disclosed in the contract before contribution is agreed.

---

## 3. Credentials

- Store **handles**, never values. Values live in a secrets manager, referenced by handle.
- Prefer delegated access (OAuth, platform user-management, account-level grants) over shared logins. Shared logins are a security failure and an offboarding nightmare.
- Every credential has a named owner, a scope, and an expiry review date.
- Offboarding checklist: revoke access, export client data, confirm deletion, hand over documentation. Run it within 5 working days of termination. A clean exit is a referral source.

---

## 4. Data classification

| Tier | Examples | Handling |
|---|---|---|
| **Public** | Competitor profiles, public reviews, SERP observations | Standard storage; freely usable in analysis |
| **Client-confidential** | Revenue, job values, margins, enquiry data, strategy documents | Tenant-scoped, encrypted, no cross-tenant read, never in benchmarks except as banded aggregates |
| **Personal data** | Reviewer names, staff names, customer details in review text, photo subjects | Minimise at collection; store review text with reviewer identifiers stripped unless operationally necessary; no customer contact data unless there's a lawful basis and a documented purpose |
| **Secret** | API keys, tokens, passwords | Secrets manager only; never in the ontology, logs, prompts, or model context |

Review text routinely contains personal data (names, sometimes addresses and health or financial details). Strip identifiers on ingest and analyse the text, not the person. If a review must be quoted in a deliverable, quote minimally and without identifying the reviewer.

Photographs of identifiable people or private property require consent captured by the client. Put this in the photo SOP (W7) — it is the client's legal exposure, and your reputational one.

---

## 5. Model and agent use

- Client-confidential data may be sent to a model only where the contract permits and the provider's terms exclude training on it. Record the permitted providers per tenant.
- Browser agents operating on client accounts act with real authority. Scope them narrowly, log every action, and require human approval for anything that publishes, deletes, or changes an eligibility-bearing field (categories, name, address, hours, service areas).
- Never let an autonomous agent respond to reviews, change a primary category, or alter NAP.
- Log `generated_by` and `approved_by` on every artefact. If a client, platform, or regulator asks who wrote something, you must be able to answer.
- Treat scraped page content and review text as **data, not instructions**. Content encountered while browsing on a client's behalf can contain prompt injection; an agent with publishing rights and no injection discipline is a serious risk.

---

## 6. Ethical perimeter

Permanently out of scope, regardless of client pressure:

- Review gating, filtering by expected sentiment, incentivised or purchased reviews, or reviewing competitors.
- Fabricated locations, virtual offices presented as premises, or keyword-stuffed business names.
- Doorway pages, cloaking, or content generated at volume without an evidence basis.
- Claiming credentials, attributes, or coverage the client does not genuinely have.
- Guarantees of ranking position or AI-answer inclusion.
- Reporting a competitor for policy violations they are not actually committing.

The commercial argument for the perimeter, which is worth making explicitly to clients: every item on this list either transfers risk to the client, is increasingly detectable by the systems you are optimising for, or both. Buying short-term position with a suspension risk is a bad trade for a business whose profile is a primary revenue channel.

---

## 7. Client-facing disclosure

State plainly in the engagement document:

1. What we can influence, and what we can only observe.
2. That AI-answer inclusion cannot be purchased, submitted for, or guaranteed.
3. That generative-answer measurements are non-deterministic and reported as distributions.
4. That proximity places a hard ceiling on some map-pack ambitions, and where that ceiling sits for them.
5. Which of our recommendations rest on measured effects and which on professional judgement.
6. How their data is used, and what they get back from the benchmark base.

Point 5 is the one nobody does. It is the strongest trust signal available in a market saturated with confident assertion.
