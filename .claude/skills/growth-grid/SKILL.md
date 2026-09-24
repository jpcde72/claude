---
name: growth-grid
description: Build or audit a Growth Grid for any brand × market. It unifies intent planning (need states as Moments), first-principles media (reach first), the Media Operating System (Reach / Transmission / Protocol layers) and the creative signal taxonomy (Moments go to market as Angles, never as audiences), plus a Delegation Gradient for agentic buying. Use on "growth grid", "unified growth system", "pilot the grid", "moments × layers", "delegation index", or any request to join intent, reach, community and agentic strategy for one brand.
---

# Growth Grid

Framework: `frameworks/growth-grid.md` (read it first). Author and IP owner: Jean-Paul Edwards. The principles are portable; any organisation named in a parent skill is an example application only.

## Parents (synced skills, run in this order)
1. `consumer-intent-modeler`: 47-intent Importance / Delivery scores (diagnose)
2. `intent-evidence-analyzer`: ground the scores in evidence (validate). Optional for a first pass
3. `first-principles-media`: who buys the category, the CEPs, the reach frontier (L1)
4. `media-operating-system`: market signature and archetypes (L2), Recommendation Equity (L3)
5. `creative-signal-taxonomy`: nine pillars and the Angle library per Moment
6. `intent-planner`: branded utilities (U), ranked by Impact × Feasibility × Data-friction

## Procedure
1. **Scope:** brand, market, category. Ask one question at most.
2. **Score intents.** Assign each intent a Moment (replenish, plan, discover, manage, celebrate, care). Leave cross-state modulators (most AGNT, some privacy and values intents) unassigned. Keep the 47 IDs exactly; flexes use `CUSTOM-`.
3. **Load into the app** (`/grids`) or compute by hand:
   - Heat(m) = Σ importance × gap / Σ importance over the Moment's intents (provisional until the canonical crosswalk exists)
   - AgenticGate = min(1, Σ AGNT-modulator delivery / Σ importance)
   - DelegationIndex(m) = prior(m) × gate
4. **Check L1 first.** Is reach at the efficient frontier across the full category buyer base? If not, that is the recommendation, whatever the rest of the grid says.
5. **Activate only hot cells.** L2 via the 2–3 signature archetypes that host the hot Moments. L3 by Heat × DI (Eligibility → Justification → Defaults). U for the top-Heat Moments only.
6. **Build the Angle library.** Every hot Moment needs Angles whose Mindset and Context pillars express it. Add a CROSS row. Run the spine check, and **sharpen, never waive**. Report white space.
7. **Guard rails:** nothing narrows who the ads reach. Moments shape creative and build, never audience. Label every prior and formula as a hypothesis. Separate what's known from what's inferred.

## Output
Grid table (Moment × Heat × DI × L1% × L3% × Angles) → L1 verdict → activated cells with a rationale → Angle library with clashes and white space → measurement per layer (mental availability per CEP; transmission proxies; Recommendation Equity per Moment; incrementality) → risks → **THE ONE THING TO DO NEXT**. Emit the app's JSON export as the companion.
