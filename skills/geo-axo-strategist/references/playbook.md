# GEO / AXO Playbook (brand edition, v2.0, as of 2026-09-26)

## 1. Diagnostic questions, in order

Ask them in this order. Each gate blocks the ones after it.

| # | Question | Workstream | If "no" |
|---|---|---|---|
| 1 | Can verified agents and retrieval crawlers reach product, price and policy pages without a challenge? | W15 | Stop. Fix the access policy first. |
| 2 | Does every SKU resolve to one identity (name, GTIN, variant) across site, feeds, retailers and marketplaces? | W1, W12 | Entity defect. Every GEO metric is noise until it is fixed. |
| 3 | Is the offer machine-legible (price, stock, shipping, returns, claims with evidence)? | W16, W12 | Agents can describe you but cannot choose you. |
| 4 | Do independent sources corroborate the brand's key claims, recently? | W5, W14 | Owned-only citation. You are fragile to a competitor with better evidence. |
| 5 | Can each priority surface complete a purchase or booking? | W16, W17 | Recommended, then routed elsewhere at checkout. |
| 6 | Is there an authoritative endpoint for agent questions? | W18 | Agents infer from third parties, errors included. |
| 7 | Once chosen, is the brand easy to keep as the default? | W19 | You win trials and lose mandates. |

## 2. Probe set (brand version)

Keep the 7 LDOS intent classes and add three agentic classes:

| Class | Example |
|---|---|
| Delegated purchase | "Buy me a [category] under [budget] that [constraint], deliver by Friday" |
| Standing mandate | "Keep me stocked on [category]; pick the best value" |
| Buyer-agent B2B | "Shortlist three [vendors] with SOC 2, EU hosting, under [budget]; explain why" |

Run the same prompts on each surface: ChatGPT, Gemini/AI Mode, Muse, Alexa for Shopping, Copilot, Perplexity. Run Siri where the action can be scripted. Use at least 3 repetitions, fresh sessions and a fixed locale. Record for each run: mentioned, shortlisted, primary, cited URLs (owned or third-party), paid unit present, completion depth reached (0–5), factual errors.

## 3. Agent journey test (per surface)

`resolve → compare → confirm price → confirm stock/slot → add to cart → pay (verified agent) → confirmation legible → return initiated`

Score the depth reached (0–7). Screen-record the attempt. Watching an agent fail to buy the client's product, live, is still the most persuasive artefact in the engagement.

## 4. Scoring ARI v2

Score each component 0–100 against the evidence, then weight:

| Component | Weight | 0 looks like | 100 looks like |
|---|---|---|---|
| Entity resolvability | 20 | Name and GTIN variants, duplicate listings | One identity everywhere, full sameAs graph |
| Claim legibility | 15 | Claims only in images or prose | Structured, evidenced, answer-shaped |
| Third-party corroboration | 20 | Owned-only citations | Recent independent evidence on every key claim |
| Access and identity | 10 | Default bot blocking | Verified agents pass; agent traffic segmented |
| Feeds and protocols | 15 | No feed, or a stale one | Complete daily feed; 2+ protocols; brand endpoint |
| Transactability | 10 | Journey depth 0–1 | Depth 6–7 on priority surfaces |
| Mandate equity | 10 | No reorder path | Subscriptions and standing options, high agent reorder rate |

Bands: 0–39 invisible to agents · 40–59 retrievable, not choosable · 60–79 choosable, partly transactable · 80–100 agent-native.

## 5. Recommendation template

`action_id · layer · arena · rung · action · why it pays in 2027 · impact H/M/L · effort H/M/L · latency · owner · KPI · evidence_ref · confidence`

## 6. Category notes

- **FMCG and consumables:** Mandate layer first (P5). Pack-size, subscription and retailer-feed parity drive the win. You need both stacks: in-wall retail media, open-web protocol work outside.
- **Retail and DTC:** Feeds and rails (A2, A4) pay back fastest. Muse and ChatGPT reward Shopify and Stripe merchants now.
- **Travel and hospitality:** AI Mode hotel booking is live (Aug 2026). Availability freshness and rate parity decide inclusion, and agent-to-agent negotiation starts here.
- **Financial services and insurance:** The claim-legibility and compliance overlap is large. Brand agents need strict grounding and disclosure (P9).
- **B2B tech and services:** W20 first. Shortlists are formed by agents before sales ever meets the buyer.
- **Local and multi-location:** Use `local-discovery-os`, with W15–W19 applied per location.

## 7. What changed from LDOS v1 geo-axo

- Added the Mandate layer and the Delegation Ladder.
- The access audit now covers agent identity (TAP, Agent Pay, Web Bot Auth), not only crawler policy.
- The readiness ladder gains rung 6: *accepts verified agent payments under a mandate*.
- ARI moves from 5 to 7 components (access split from feeds; Mandate equity added).
- Probe engines list: Muse, Alexa for Shopping and Siri added; results reported per surface.
