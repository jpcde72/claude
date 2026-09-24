from app.models import Angle, IntentDomain, IntentScore, Moment
from app.services.grid_service import (
    agentic_gate,
    create_grid,
    export_json,
    moment_heat,
    spine_clashes,
    summarise,
)


def score(tid, domain, moment, imp, dlv):
    return IntentScore(
        taxonomy_id=tid, name=tid, domain=domain, moment=moment, importance=imp, delivery=dlv
    )


def test_heat_is_importance_weighted_mean_gap():
    intents = [
        score("FUNC-01", IntentDomain.FUNC, Moment.REPLENISH, 80, 50),  # gap 30
        score("CTXT-01", IntentDomain.CTXT, Moment.REPLENISH, 20, 30),  # gap -10
    ]
    heat = moment_heat(intents)
    assert heat[Moment.REPLENISH] == ((80 * 30 + 20 * -10) / 100, 2)
    assert heat[Moment.CARE] == (0.0, 0)


def test_modulators_gate_delegation_but_do_not_heat():
    intents = [
        score("AGNT-01", IntentDomain.AGNT, None, 80, 40),
        score("AGNT-02", IntentDomain.AGNT, None, 20, 10),
    ]
    assert agentic_gate(intents) == 0.5
    assert all(n == 0 for _, n in moment_heat(intents).values())


def test_gate_is_none_without_agnt_modulators():
    assert agentic_gate([score("AGNT-01", IntentDomain.AGNT, Moment.PLAN, 80, 40)]) is None


def test_spine_clash_ignores_case_and_whitespace():
    angles = [
        Angle(name="A", mindset="Analytical", messaging="Value"),
        Angle(name="B", mindset="analytical ", messaging="value"),
        Angle(name="C", mindset="Analytical", messaging="Craft"),
    ]
    assert spine_clashes(angles) == [("A", "B")]


def test_summary_shares_and_white_space(db):
    grid = create_grid(db, "Brand", "UK", "Grocery", None)
    grid.intent_scores += [
        score("FUNC-01", IntentDomain.FUNC, Moment.REPLENISH, 90, 50),
        score("EMOT-01", IntentDomain.EMOT, Moment.CELEBRATE, 90, 50),
        score("AGNT-01", IntentDomain.AGNT, None, 100, 100),
    ]
    grid.angles.append(Angle(name="Party", moment=Moment.CELEBRATE, mindset="Joy", messaging="Share"))
    db.commit()

    s = summarise(grid)
    rows = {r.moment: r for r in s.rows}
    assert s.agentic_gate == 1.0
    assert rows[Moment.REPLENISH].delegation_index == 0.8
    # Same CEP weight, higher delegation -> more protocol effort, less memory emphasis.
    assert rows[Moment.REPLENISH].l3_share > rows[Moment.CELEBRATE].l3_share
    assert rows[Moment.REPLENISH].l1_share < rows[Moment.CELEBRATE].l1_share
    assert round(sum(r.l1_share for r in s.rows)) == 100
    assert round(sum(r.l3_share for r in s.rows)) == 100
    # Even a fully delegated Moment keeps some memory emphasis.
    assert rows[Moment.REPLENISH].l1_share > 0
    assert rows[Moment.REPLENISH].role == "fix" and rows[Moment.CARE].role == "hold"
    assert rows[Moment.REPLENISH].white_space and not rows[Moment.CELEBRATE].white_space

    out = export_json(grid)
    assert out["need_state_heat"]["replenish"] == 40.0
    assert out["angles"][0]["moment"] == "celebrate"


def test_strength_keeps_memory_emphasis(db):
    """A Moment the brand over-delivers on is led with, not starved (Truth 1)."""
    grid = create_grid(db, "Brand", "UK", "Grocery", None)
    grid.intent_scores += [
        score("FUNC-01", IntentDomain.FUNC, Moment.PLAN, 60, 30),       # gap +30
        score("EMOT-01", IntentDomain.EMOT, Moment.CELEBRATE, 60, 90),  # gap -30
    ]
    db.commit()
    rows = {r.moment: r for r in summarise(grid).rows}
    assert rows[Moment.CELEBRATE].role == "leverage"
    assert rows[Moment.CELEBRATE].l1_share > rows[Moment.PLAN].l1_share
    assert rows[Moment.CELEBRATE].white_space


def test_grid_routes_end_to_end(client):
    r = client.post("/grids", data={"brand": "Acme", "market": "UK", "category": "Pet food"})
    assert r.status_code == 200 and "Acme" in r.text

    r = client.get("/grids/1")
    assert r.status_code == 200 and "Replenish" in r.text

    r = client.post(
        "/grids/1/intents",
        data={"taxonomy_id": "func-01", "name": "Task completion", "domain": "FUNC",
              "moment": "replenish", "importance": 150, "delivery": 40},
    )
    assert r.status_code == 200 and "FUNC-01" in r.text

    for name in ("One", "Two"):
        client.post("/grids/1/angles", data={"name": name, "moment": "", "mindset": "M", "messaging": "X"})
    r = client.get("/grids/1")
    assert "Spine clash" in r.text

    r = client.put("/grids/1/priors", data={"prior_replenish": "0.9"})
    assert r.status_code == 200

    data = client.get("/grids/1/export.json").json()
    assert data["intents"][0]["importance"] == 100  # clamped
    assert data["moments"][0]["delegation_prior"] == 0.9
    assert data["spine_clashes"] == [["One", "Two"]]
    assert client.get("/grids/99/export.json").status_code == 404


def test_import_grid_round_trips(db):
    from app.services.grid_service import import_grid

    grid = import_grid(db, {
        "meta": {"brand": "B", "market": "UK", "category": "Grocery"},
        "delegation_priors": {"care": 0.3},
        "intents": [{"taxonomy_id": "AGNT-P01", "name": "Delegation", "domain": "AGNT",
                     "moment": None, "importance": 40, "delivery": 20}],
        "angles": [{"name": "X", "moment": "CROSS", "mindset": "M", "messaging": "Y"}],
    })
    out = export_json(grid)
    assert out["agentic_gate"] == 0.5
    assert [m["delegation_prior"] for m in out["moments"] if m["moment"] == "care"] == [0.3]
    assert out["angles"][0]["moment"] == "CROSS"
