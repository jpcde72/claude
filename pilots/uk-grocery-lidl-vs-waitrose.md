# Growth Grid pilot: Lidl GB vs Waitrose (UK grocery)

*Growth Grid v0.3 · 24 Sep 2026 · Framework and IP: Jean-Paul Edwards. The brands are an example application; no client work is involved.*
*Data: `pilots/lidl_uk.json`, `pilots/waitrose_uk.json` → exports `*.export.json`. Reload with `python scripts/load_pilot.py pilots/*_uk.json`.*

---

## Headline

**Both brands' hottest Moment falls where agents will decide first (Replenish/Plan). They fail there for opposite reasons.**

- **Lidl has a price justification and no eligibility.** It would win an agent's price comparison, but agents can't buy from it: there's no online grocery checkout (Agentic Gate 0.51).
- **Waitrose has eligibility and no price justification.** Agents can transact with it (online grocery, Gate 0.94), but its weekly-shop price perception loses the comparison (Replenish Heat +14.6, driven by Budget fit, gap +45).

So the same grid prescribes different L3 work: **Lidl needs to become visible to agents; Waitrose needs to become provable to them.**

---

## 1. The evidence base

| | Lidl GB | Waitrose | Status |
|---|---|---|---|
| Share, 12 weeks to 9 Aug 2026 | 8.8%, sales +8.5% YoY; overtook Morrisons for #5 | 4.5%, sales +2.8% YoY | Known (Worldpanel, via [Grocery Gazette](https://www.grocerygazette.co.uk/2026/07/21/lidl-leads-grocery-market-share-growth/), [The Grocer](https://www.thegrocer.co.uk/news/lidl-sails-past-morrisons-to-become-uks-fifth-biggest-supermarket/719385.article), [andrewdremin.com](https://andrewdremin.com/uk-grocery-market-share-2026/)) |
| Online grocery | None. Stores plus Lidl Plus; non-food web shop only | ~160k home deliveries/week; 1,400 vans; AI route optimisation (Satalia) | Known ([Retail Gazette, Mar 2026](https://www.retailgazette.co.uk/blog/2026/03/waitrose-ai-satalia-optimisation/)); Lidl: secondary ([delivercart](https://delivercart.co.uk/blog/lidl-delivery-in-the-uk/)) |
| App | Lidl Plus: daily active users +20% YoY; points added May 2026; coupon investment +60%; Lidl & Go scan-and-go rolling out to 37 more stores | App with AI recommendations | Known ([The Grocer](https://www.thegrocer.co.uk/news/lidl-plus-app-users-unfazed-by-loyalty-scheme-overhaul/720013.article), [Lidl GB](https://corporate.lidl.co.uk/media-centre/pressreleases/2026/lidl-and-go-roll-out)); Waitrose "45% get AI recs" is a vendor claim ([CX Network](https://www.cxnetwork.com/artificial-intelligence/articles/waitrose-personalization-ai)) |
| Agent access, category-wide | UK grocers offer no developer APIs; Tesco is building an AI basket-builder (Adobe, Mistral); ChatGPT agent mode is being trialled against grocers | Same | Known, secondary ([Forbes, Aug 2026](https://www.forbes.com/sites/bernardmarr/2026/08/12/tescos-ai-agents-could-soon-do-your-shopping-for-you/), [Retail Week](https://www.retail-week.com/technology/chatgpt-agent-mode-on-trial-how-sainsburys-wickes-and-more-handle-ai-as-a-customer/7049409.article), [open-supermarkets](https://github.com/abracadabra50/uk-grocery-cli)) |

**Scoring method:**
- **Importance** is category-level (UK grocery 2026) and **identical for both brands**, so every difference comes from **delivery**.
- **Delivery** scores are analyst judgement anchored to the evidence above: **inferred**, confidence medium.
- **Intent IDs are provisional** (`-P` suffix) until the canonical `taxonomy.md` is added.

---

## 2. The two grids

| Moment | Lidl Heat | Lidl role | Waitrose Heat | Waitrose role | CEP weight | DI Lidl / Waitrose |
|---|---|---|---|---|---|---|
| Replenish | +8.0 | fix | **+14.6** | **fix** | 300 | 0.41 / 0.75 |
| Plan | **+11.2** | **fix** | +2.0 | hold | 190 | 0.33 / 0.61 |
| Discover | −15.7 | leverage | −20.7 | leverage | 105 | 0.23 / 0.42 |
| Manage | −3.8 | hold | +2.6 | hold | 170 | 0.26 / 0.47 |
| Celebrate | +1.8 | hold | **−25.2** | **leverage** | 165 | 0.10 / 0.19 |
| Care | −0.6 | hold | **−18.8** | **leverage** | 165 | 0.08 / 0.14 |
| **Agentic Gate** | **0.51** | | **0.94** | | | |

**L1 memory emphasis (%)**

| | Replenish | Plan | Discover | Manage | Celebrate | Care |
|---|---|---|---|---|---|---|
| Lidl | 22.8 | 16.0 | 9.9 | 15.5 | 17.8 | 18.1 |
| Waitrose | 16.2 | 13.9 | 10.4 | 15.6 | 21.4 | 22.5 |

**How to read the grid:**
- **Lidl's grid is a price machine with a planning hole.** It over-delivers on Discover (the Middle of Lidl) and holds everywhere else. Its gaps sit in Plan (cognitive offload: no lists or baskets, gap +25) and Replenish (range and availability, and the "second shop" problem).
- **Waitrose's grid is a strength machine with a weekly-shop hole.** It leads on Celebrate, Care and Discover. Its one real gap is **Budget fit in Replenish**, which also appears as cost-of-living anxiety (+35) in Manage.
- **Because Waitrose's gate is higher, more of every Moment is decided by agents.** Waitrose's Replenish is 75% delegated vs Lidl's 41%. So Waitrose's price gap is **more exposed to machine comparison** than Lidl's planning gap is.

---

## 3. Layer by layer

### L1 Reach (First Principles): check this first
- **Lidl:** growth is coming from penetration: +8.5% sales, and it overtook Morrisons. This fits Truths 2 and 3. **Verdict: keep funding broad reach.** The risk is its upmarket London push drifting into *targeting* posh postcodes instead of reaching everyone (inferred).
- **Waitrose:** growth is +2.8%, below the market leaders. The typical inherited assumption is "our affluent core". Truth 2 says growth comes from **light and non-buyers** (Aldi, Lidl and Tesco shoppers who trade up occasionally). **Verdict: reach is likely under-built for the buyer base it needs.** Test it: Waitrose penetration vs Lidl's, and whether the media plan's reach is capped by affluence targeting. *Data missing: no reach or penetration figures retrieved.*

### L2 Transmission (UK signature: Place-bound Civic + Identity Tribe + Gatekeeper)
| Archetype | Lidl | Waitrose |
|---|---|---|
| Place-bound Civic | New store openings as local events. Show up at the address | Village and high-street anchor. John Lewis Partnership as a civic institution |
| Identity Tribe | "Savvy shopper" and Middle-of-Lidl fandom: haul UGC, creators. Service the tribe, don't wear it | Foodie and host identity. The risk is class costume: speak to the *occasion*, not the class |
| Gatekeeper | **Which?**-style price comparisons and press price checks: *write for the gatekeeper*. Price proof is already structured for it | Food editors and Waitrose Food: authority on quality. **New gatekeeper: agents doing price comparison** |

### L3 Protocol (Recommendation Equity)
| Arena | Lidl (gate 0.51): get **eligible** | Waitrose (gate 0.94): get **justified** |
|---|---|---|
| Eligibility | **Agent-planned, store-fulfilled.** Publish structured price, range and store-stock feeds so agents can *plan a Lidl shop* even without an online checkout. Make Lidl Plus lists and coupons machine-readable | Already transactable. Keep product data complete and consistent across Waitrose.com, Ocado-style comparisons and AI answers |
| Justification | Already strong on price. Make the proof verifiable (dated basket prices) | **The fight.** A verifiable value claim on staples (Essentials range; basket-level comparisons), so an agent can defend choosing Waitrose on price per quality |
| Defaults | Weekly-plan defaults inside Lidl Plus | Subscription and "usual shop" defaults. Protect the repeat basket before agents re-optimise it |

### Angles (Creative Signal)
- **Lidl:** 6 Angles (1 CROSS). No clashes, no white space. **Gap:** Manage has no Angle. That's fine (hold), but cost-of-living anxiety is Lidl's biggest over-delivery on one intent (−10), so it could be a CROSS candidate.
- **Waitrose:** 7 Angles (1 CROSS).
  - **Clash caught and sharpened:** "Partnership Standards" (CROSS) vs "Free-From Without the Fuss" were both Health-conscious × Health/functional benefit. The fix exposed a **vocabulary gap**: the Messaging pillar has no *provenance/standards* value, so Waitrose's biggest asset couldn't be expressed. Logged as `Provenance/standards [CUSTOM]`, a candidate pillar revision.
  - **White space: Care.** Waitrose's strongest leverage Moment has no dedicated Angle. It only exists as the general CROSS argument. **Candidate: "Feed Them Well"** (Caring-parent mindset × Provenance/standards × sourcing certification × family meal table).

### U Utilities (intent-planner; only for fix Moments)
- **Lidl:** **Plan** — a Lidl Plus weekly planner: meal plan → list → coupons → store-stock check. Uses Tier 1–2 data only. It fixes the cognitive-offload gap without building e-commerce.
- **Waitrose:** **Replenish** — a "usual shop, value-checked" utility that shows the basket against a comparison on staples and swaps to Essentials where equivalent. It turns the price gap into proof.

---

## 4. Measurement
| Layer | Lidl | Waitrose |
|---|---|---|
| L1 | Mental availability for Plan/Replenish CEPs; reach vs frontier | Penetration among light buyers; mental availability for weekly-shop CEPs (not just occasions) |
| L2 | Earned haul/UGC volume; store-opening local reach | Editor/authority mentions; share of hosting conversation |
| L3 | **Eligibility rate:** % of agent meal-plan queries that surface Lidl | **Justification win-rate:** % of agent basket comparisons where Waitrose is selected or defended |
| Causal | Geo-holdout on the planner utility | Incrementality test on value-proof creative |

---

## 5. What the pilot taught the framework (v0.2 → v0.3)
1. **Formula fix.** v0.2 weighted L1 memory emphasis by *gap*, which starved Waitrose's strengths (~1.6% emphasis on Celebrate and Care). That breaks Truth 1. **v0.3:** L1 and L3 emphasis follow **CEP weight** (the Moment's size in the category), split by delegation. Heat now only sets the Moment's **role** (fix / hold / leverage).
2. **Vocabulary gap** in the creative signal Messaging pillar: *Provenance/standards*.
3. **Provisional intent IDs** need the canonical `taxonomy.md` and crosswalk before any client use.
4. **L3 shares come out almost identical across brands.** That's expected, because the gate scales every Moment equally. Brands differ in the **gate level** and the **arena** they need to work on, which the table in §3 captures. Consider whether per-Moment agent evidence (agent-referred share by Moment) should replace the uniform gate.

## 6. Risks
- **Delivery scores are judgement.** Run `intent-evidence-analyzer` before trusting the ranking. The headline depends mainly on Budget fit (Waitrose) and Cognitive offload plus System compatibility (Lidl), and those are the least disputable scores.
- **The Delegation priors are untested.** UK grocery agent checkout is still pre-API (low confidence on timing).
- **Lidl's store-only model may be a feature, not a gap.** Low cost-to-serve funds the price leadership. The recommendation is agent *planning* eligibility, not e-commerce.

**THE ONE THING TO DO NEXT:** get the canonical `taxonomy.md` and crosswalk into the repo, then re-score both pilots with evidence. The headline finding is only as strong as those Budget-fit and System-compatibility scores.
