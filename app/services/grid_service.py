"""Growth Grid calculations. See frameworks/growth-grid.md.

Formulas here are provisional: heat stands in for the intent->need-state
crosswalk until the canonical crosswalk file is added, and the delegation
priors are hypotheses to validate against agent-referred share per Moment.
"""

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models import Angle, Grid, IntentDomain, IntentScore, Moment, MomentSetting

DEFAULT_DELEGATION_PRIORS: dict[Moment, float] = {
    Moment.REPLENISH: 0.80,
    Moment.PLAN: 0.65,
    Moment.DISCOVER: 0.45,
    Moment.MANAGE: 0.50,
    Moment.CELEBRATE: 0.20,
    Moment.CARE: 0.15,
}

MOMENT_QUESTIONS: dict[Moment, str] = {
    Moment.REPLENISH: "We're running low.",
    Moment.PLAN: "What are we doing this week?",
    Moment.DISCOVER: "Show me something new.",
    Moment.MANAGE: "This needs handling.",
    Moment.CELEBRATE: "This matters.",
    Moment.CARE: "This is my responsibility.",
}

# Every Moment keeps some memory-building creative weight: humans still set
# the agent's rules, and a share of buyers will never delegate.
L1_FLOOR = 0.15

# Heat thresholds for a Moment's role. Heat decides what to fix or lead with,
# never how much memory-building a Moment gets (that follows CEP size, Truth 1).
FIX_AT = 5.0
LEVERAGE_AT = -10.0


@dataclass
class MomentRow:
    moment: Moment
    question: str
    heat: float  # importance-weighted mean gap; >0 = under-delivery = opportunity
    role: str  # fix | hold | leverage
    cep_weight: int  # total category importance of the Moment's intents
    intent_count: int
    delegation_prior: float
    delegation_index: float
    l1_share: float  # share of L1 creative/CEP emphasis (not L1 budget)
    l3_share: float  # share of L3 protocol build effort
    angle_count: int
    white_space: bool  # fix or leverage Moment with no dedicated Angle


@dataclass
class GridSummary:
    rows: list[MomentRow]
    agentic_gate: float | None  # None = no AGNT modulators scored
    spine_clashes: list[tuple[str, str]] = field(default_factory=list)
    cross_angle_count: int = 0


def create_grid(db: Session, brand: str, market: str, category: str, notes: str | None) -> Grid:
    grid = Grid(brand=brand, market=market, category=category, notes=notes)
    grid.moment_settings = [
        MomentSetting(moment=m, delegation_prior=p) for m, p in DEFAULT_DELEGATION_PRIORS.items()
    ]
    db.add(grid)
    db.commit()
    db.refresh(grid)
    return grid


def moment_role(heat: float) -> str:
    if heat >= FIX_AT:
        return "fix"
    if heat <= LEVERAGE_AT:
        return "leverage"
    return "hold"


def moment_heat(intents: list[IntentScore]) -> dict[Moment, tuple[float, int]]:
    """Importance-weighted mean gap per Moment. Modulators are excluded."""
    result: dict[Moment, tuple[float, int]] = {}
    for m in Moment:
        members = [i for i in intents if i.moment == m]
        weight = sum(i.importance for i in members)
        heat = sum(i.importance * i.gap for i in members) / weight if weight else 0.0
        result[m] = (round(heat, 1), len(members))
    return result


def agentic_gate(intents: list[IntentScore]) -> float | None:
    """How far agentic trust is delivered relative to how much it matters (0-1).

    AGNT intents mostly act as cross-state modulators: a gap here gates
    delegation in every Moment rather than heating one.
    """
    agnt = [i for i in intents if i.domain == IntentDomain.AGNT and i.is_modulator]
    importance = sum(i.importance for i in agnt)
    if not importance:
        return None
    return round(min(1.0, sum(i.delivery for i in agnt) / importance), 2)


def spine_clashes(angles: list[Angle]) -> list[tuple[str, str]]:
    """Pairwise spine check: same mindset x messaging = a reskin with no added extension."""
    def key(a: Angle) -> tuple[str, str]:
        return (a.mindset.strip().lower(), a.messaging.strip().lower())

    return [
        (a.name, b.name)
        for i, a in enumerate(angles)
        for b in angles[i + 1 :]
        if key(a) == key(b)
    ]


def _shares(weights: dict[Moment, float]) -> dict[Moment, float]:
    total = sum(weights.values())
    return {m: round(100 * w / total, 1) if total else 0.0 for m, w in weights.items()}


def summarise(grid: Grid) -> GridSummary:
    heat = moment_heat(grid.intent_scores)
    gate = agentic_gate(grid.intent_scores)
    priors = {s.moment: s.delegation_prior for s in grid.moment_settings}
    di = {m: round(priors.get(m, 0.0) * (gate if gate is not None else 1.0), 2) for m in Moment}

    # Emphasis follows the size of the Moment in the category (CEP weight),
    # split by who decides it: people (L1 memory) or agents (L3 protocol).
    # L1 reach itself is never cut here.
    cep = {m: sum(i.importance for i in grid.intent_scores if i.moment == m) for m in Moment}
    l1 = _shares({m: cep[m] * (1 - di[m] + L1_FLOOR) for m in Moment})
    l3 = _shares({m: cep[m] * di[m] for m in Moment})
    roles = {m: moment_role(heat[m][0]) for m in Moment}

    angle_counts = {m: sum(1 for a in grid.angles if a.moment == m) for m in Moment}
    rows = [
        MomentRow(
            moment=m,
            question=MOMENT_QUESTIONS[m],
            heat=heat[m][0],
            role=roles[m],
            cep_weight=cep[m],
            intent_count=heat[m][1],
            delegation_prior=priors.get(m, 0.0),
            delegation_index=di[m],
            l1_share=l1[m],
            l3_share=l3[m],
            angle_count=angle_counts[m],
            white_space=roles[m] != "hold" and angle_counts[m] == 0,
        )
        for m in Moment
    ]
    return GridSummary(
        rows=rows,
        agentic_gate=gate,
        spine_clashes=spine_clashes(grid.angles),
        cross_angle_count=sum(1 for a in grid.angles if a.moment is None),
    )


def export_json(grid: Grid) -> dict:
    """JSON companion aligned with the intent-planner v2.0 schema where they overlap."""
    s = summarise(grid)
    return {
        "meta": {
            "brand": grid.brand,
            "market": grid.market,
            "category": grid.category,
            "framework": "growth-grid",
            "version": "0.3",
            "source": "pipeline",
        },
        "need_state_heat": {r.moment.value: r.heat for r in s.rows},
        "agentic_gate": s.agentic_gate,
        "moments": [
            {
                "moment": r.moment.value,
                "heat": r.heat,
                "role": r.role,
                "cep_weight": r.cep_weight,
                "delegation_prior": r.delegation_prior,
                "delegation_index": r.delegation_index,
                "l1_creative_share": r.l1_share,
                "l3_protocol_share": r.l3_share,
                "angles": r.angle_count,
                "white_space": r.white_space,
            }
            for r in s.rows
        ],
        "intents": [
            {
                "taxonomy_id": i.taxonomy_id,
                "name": i.name,
                "domain": i.domain.value,
                "primary_state": i.moment.value if i.moment else None,
                "modulator": i.is_modulator,
                "importance": i.importance,
                "delivery": i.delivery,
                "gap": i.gap,
            }
            for i in grid.intent_scores
        ],
        "angles": [
            {
                "name": a.name,
                "moment": a.moment.value if a.moment else "CROSS",
                "mindset": a.mindset,
                "messaging": a.messaging,
                "proof": a.proof,
                "context": a.context,
            }
            for a in grid.angles
        ],
        "spine_clashes": [list(c) for c in s.spine_clashes],
    }


def import_grid(db: Session, data: dict) -> Grid:
    """Create a grid from a pilot definition (see pilots/*.json)."""
    meta = data["meta"]
    grid = create_grid(db, meta["brand"], meta["market"], meta["category"], meta.get("notes"))
    priors = data.get("delegation_priors", {})
    for s in grid.moment_settings:
        if s.moment.value in priors:
            s.delegation_prior = float(priors[s.moment.value])
    for i in data.get("intents", []):
        grid.intent_scores.append(
            IntentScore(
                taxonomy_id=i["taxonomy_id"],
                name=i["name"],
                domain=IntentDomain(i["domain"]),
                moment=Moment(i["moment"]) if i.get("moment") else None,
                importance=i["importance"],
                delivery=i["delivery"],
            )
        )
    for a in data.get("angles", []):
        grid.angles.append(
            Angle(
                name=a["name"],
                moment=Moment(a["moment"]) if a.get("moment") not in (None, "", "CROSS") else None,
                mindset=a["mindset"],
                messaging=a["messaging"],
                proof=a.get("proof"),
                context=a.get("context"),
            )
        )
    db.commit()
    db.refresh(grid)
    return grid
