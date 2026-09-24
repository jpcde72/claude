"""Build the Growth Grid pilot reports (Tropical Sunrise house style) from pilot exports.

Usage: python scripts/build_reports.py
Reads pilots/*_uk.json + *.export.json, writes reports/*.html.
"""

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PILOTS = ROOT / "pilots"
OUT = ROOT / "reports"

FIX_AT, LEVERAGE_AT = 5.0, -10.0
MOMENT_Q = {
    "replenish": "We're running low.",
    "plan": "What are we doing this week?",
    "discover": "Show me something new.",
    "manage": "This needs handling.",
    "celebrate": "This matters.",
    "care": "This is my responsibility.",
}

e = html.escape

# ---------------------------------------------------------------- brand context
BRANDS = {
    "lidl": {
        "file": "lidl_uk",
        "title": "Lidl GB",
        "page_title": "Lidl Growth Grid",
        "gradient_word": "eligible",
        "thesis": "Lidl wins the price argument an agent would run. It just isn't in the room when the agent runs it.",
        "takeaway_label": "Agentic Gate",
        "stats": [
            ("8.8%", "GB grocery share, 12 wks to 9 Aug 2026"),
            ("+8.5%", "Sales growth YoY; now the #5 grocer"),
            ("0", "Online grocery checkouts an agent can use"),
        ],
        "diagnosis": [
            "Lidl's grid is a price machine with a planning hole. It over-delivers on Discover (the Middle of Lidl) and on cost-of-living reassurance, and holds everywhere else.",
            "The gaps sit in <b>Plan</b> (no lists, baskets or planning help: cognitive offload gap +25) and <b>Replenish</b> (range and availability drive a second shop elsewhere).",
            "Both gaps sit in the Moments agents will take first. With no online grocery and no machine-readable range, the Agentic Gate is <b>0.51</b>, so agents can plan around Lidl but not with it.",
        ],
        "layers": [
            ("L1 · Reach", "Keep funding broad reach",
             "Growth is coming from penetration (+8.5%, overtaking Morrisons). This matches the light-buyer maths. Guard against the upmarket push turning into postcode targeting: Moments shape the creative, never who sees it."),
            ("L2 · Transmission", "Write for the price gatekeepers",
             "UK signature: Place-bound Civic + Identity Tribe + Gatekeeper. Store openings are local events. Serve the savvy-shopper and Middle-of-Lidl tribe with haul and creator content. Published price comparisons are the gatekeeper, and Lidl's proof is already structured for them."),
            ("L3 · Protocol", "Get eligible: agent-planned, store-fulfilled",
             "Publish structured price, range and store-stock feeds so an agent can plan a Lidl shop without an online checkout. Make Lidl Plus lists and coupons machine-readable. Justification (price) is already strong; defaults can live in a Lidl Plus weekly plan."),
            ("U · Utility", "A weekly planner inside Lidl Plus",
             "Meal plan → list → coupons → store-stock check. Uses Tier 1–2 data only. It fixes the Plan gap without building e-commerce, which would erode the cost base that pays for the price lead."),
        ],
        "measure": [
            ("L1", "Mental availability for weekly-shop and planning entry points; reach against the efficient frontier"),
            ("L2", "Earned haul and creator volume; local reach of store openings"),
            ("L3", "Eligibility rate: share of agent meal-plan queries that surface Lidl"),
            ("Causal", "Geo-holdout test of the planner utility"),
        ],
        "white_note": "No white space. Manage has no Angle, which is fine for a hold Moment, but cost-of-living reassurance is Lidl's biggest single over-delivery and could earn a CROSS Angle.",
        "next": "Scope the Lidl Plus planner and a public store-stock feed as one build. It closes the Plan gap and the eligibility gap together.",
        "sources": [
            ("Grocery Gazette — Lidl leads market share growth (Jul 2026)", "https://www.grocerygazette.co.uk/2026/07/21/lidl-leads-grocery-market-share-growth/"),
            ("The Grocer — Lidl overtakes Morrisons", "https://www.thegrocer.co.uk/news/lidl-sails-past-morrisons-to-become-uks-fifth-biggest-supermarket/719385.article"),
            ("The Grocer — Lidl Plus daily users +20%", "https://www.thegrocer.co.uk/news/lidl-plus-app-users-unfazed-by-loyalty-scheme-overhaul/720013.article"),
            ("Lidl GB — Lidl & Go rolls out to 37 stores", "https://corporate.lidl.co.uk/media-centre/pressreleases/2026/lidl-and-go-roll-out"),
            ("Delivercart — no Lidl GB home grocery delivery (secondary)", "https://delivercart.co.uk/blog/lidl-delivery-in-the-uk/"),
        ],
    },
    "waitrose": {
        "file": "waitrose_uk",
        "title": "Waitrose",
        "page_title": "Waitrose Growth Grid",
        "gradient_word": "provable",
        "thesis": "Agents can already buy from Waitrose. On the weekly shop, they can't yet justify choosing it.",
        "takeaway_label": "Replenish Heat",
        "stats": [
            ("4.5%", "GB grocery share, 12 wks to 9 Aug 2026"),
            ("+2.8%", "Sales growth YoY, below the leaders"),
            ("160k", "Home deliveries a week: transactable by design"),
        ],
        "diagnosis": [
            "Waitrose's grid is a strength machine with a weekly-shop hole. It leads on <b>Celebrate</b>, <b>Care</b> and <b>Discover</b>, the Moments where quality, provenance and hosting matter.",
            "Its one real gap is <b>Budget fit</b> in Replenish (gap +45). The same gap shows up again as cost-of-living anxiety (+35) in Manage.",
            "The Agentic Gate is high (<b>0.94</b>), so 75% of Replenish is modelled as agent-decided. Agents compare price in exactly that Moment, which leaves the gap exposed to machine comparison.",
        ],
        "layers": [
            ("L1 · Reach", "Reach past the affluent core",
             "Growth of +2.8% trails the leaders. Growth comes from light and non-buyers who trade up now and then, not from a sharper affluent target. Test penetration and whether reach is capped by affluence targeting. Reach and penetration data were not retrieved for this pilot."),
            ("L2 · Transmission", "Speak to the occasion, not the class",
             "The Place-bound Civic archetype favours the high-street anchor and the Partnership as a civic institution. For the foodie and host tribe, avoid class costume. Food editors are the human gatekeepers; price-comparing agents are the new ones."),
            ("L3 · Protocol", "Get justified: make value provable",
             "Already eligible. The fight is in Justification: a verifiable value claim on staples (the Essentials range, basket-level comparisons) that an agent can defend. Protect repeat-basket defaults before agents re-optimise them."),
            ("U · Utility", "A “usual shop, value-checked” utility",
             "Shows the weekly basket against a comparison on staples and swaps to Essentials where equivalent. It turns the price gap into proof, using Tier 2 order history."),
        ],
        "measure": [
            ("L1", "Penetration among light buyers; mental availability for weekly-shop entry points, not just occasions"),
            ("L2", "Authority and editor mentions; share of the hosting conversation"),
            ("L3", "Justification win rate: share of agent basket comparisons where Waitrose is chosen or defended"),
            ("Causal", "Incrementality test of value-proof creative"),
        ],
        "white_note": "White space in <b>Care</b>: the strongest leverage Moment has no dedicated Angle, so it only appears as the general CROSS argument. Candidate: <b>Feed Them Well</b> (caring-parent mindset × provenance/standards × sourcing certification × family meal table).",
        "next": "Build the value-proof Angle and the value-checked basket together, so the weekly shop has an argument an agent can repeat.",
        "sources": [
            ("Grocery Gazette — Worldpanel shares (Jul 2026)", "https://www.grocerygazette.co.uk/2026/07/21/lidl-leads-grocery-market-share-growth/"),
            ("Retail Gazette — Waitrose AI route optimisation (Mar 2026)", "https://www.retailgazette.co.uk/blog/2026/03/waitrose-ai-satalia-optimisation/"),
            ("CX Network — Waitrose AI personalisation (vendor claim)", "https://www.cxnetwork.com/artificial-intelligence/articles/waitrose-personalization-ai"),
            ("Forbes — Tesco AI agents (Aug 2026)", "https://www.forbes.com/sites/bernardmarr/2026/08/12/tescos-ai-agents-could-soon-do-your-shopping-for-you/"),
            ("Retail Week — ChatGPT agent mode vs retailers", "https://www.retail-week.com/technology/chatgpt-agent-mode-on-trial-how-sainsburys-wickes-and-more-handle-ai-as-a-customer/7049409.article"),
        ],
    },
}


# Published report URLs, filled after the first publish so the pages cross-link.
URLS: dict[str, str] = {}
URLS_FILE = ROOT / "reports" / "urls.json"
if URLS_FILE.exists():
    URLS = json.loads(URLS_FILE.read_text())


def links(other):
    name = BRANDS[other]["title"]
    o = f'<a href="{URLS[other]}">{name} report</a>' if other in URLS else f"{name} report"
    d = f'<a href="{URLS["diagnostic"]}">diagnostic report</a>' if "diagnostic" in URLS else "diagnostic report"
    return f"Compare with the {o}, and see the {d} for why the two grids differ."


def brand_links():
    return "".join(f'<a href="{URLS[k]}">{BRANDS[k]["title"]} report</a>' for k in ("lidl", "waitrose") if k in URLS)


def load(key):
    b = BRANDS[key]
    src = json.loads((PILOTS / f"{b['file']}.json").read_text())
    exp = json.loads((PILOTS / f"{b['file']}.export.json").read_text())
    return src, exp


# ---------------------------------------------------------------- shared chrome
CSS = """
:root{
  --violet:#4B2E83;--purple:#7B3FAB;--magenta:#C026A0;--coral:#F05A28;--pink:#F78DA7;--solar:#FFCC00;
  --lilac:#B08AE0;--bg:#0A0A0A;--panel:#141414;--panel2:#1B1B1B;--line:#262626;--ink:#FFFFFF;--ink2:#B0B0B0;--ink3:#7A7A7A;
  color-scheme:dark;
}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:"Outfit",Helvetica,Arial,sans-serif;font-weight:300;font-size:16px;line-height:1.6;margin:0}
.bar{height:6px;background:linear-gradient(90deg,var(--violet),var(--purple),var(--magenta),var(--coral),var(--pink),var(--solar))}
.wrap{max-width:1080px;margin:0 auto;padding-inline:clamp(16px,4vw,48px);padding-block:40px 64px;display:grid;gap:56px}
.kicker,.label,th,.mono{font-family:"Space Mono","Courier New",monospace;text-transform:uppercase;letter-spacing:.25em;font-size:11px;color:var(--ink2);font-weight:400}
h1,h2,h3{font-family:"Fraunces",Georgia,serif;font-weight:400;text-wrap:balance;margin:0;line-height:1.1}
h1{font-size:clamp(44px,8vw,88px)}
h2{font-size:clamp(28px,4vw,40px)}
h3{font-family:"Outfit",sans-serif;font-weight:500;font-size:19px;line-height:1.3}
.grad{font-style:italic;background:linear-gradient(90deg,var(--magenta),var(--coral),var(--solar));-webkit-background-clip:text;background-clip:text;color:transparent}
p{margin:0;max-width:68ch;color:var(--ink2)}
p b,li b{color:var(--ink);font-weight:500}
.hero{display:grid;gap:20px;position:relative}
.hero .thesis{font-size:clamp(19px,2.4vw,24px);color:var(--ink);max-width:40ch;font-weight:300}
.mark{position:absolute;right:0;top:-10px;width:min(420px,55%);opacity:.9;pointer-events:none}
.mark path{fill:none;stroke-width:3;stroke-linecap:round}
.section{display:grid;gap:24px}
.section>header{display:grid;gap:10px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1px;background:var(--line);border-radius:14px;overflow:hidden}
.stat{background:var(--panel);padding:22px;display:grid;gap:6px;align-content:start}
.stat .n{font-weight:600;font-size:clamp(34px,5vw,48px);line-height:1;font-variant-numeric:tabular-nums}
.stat.take .n{color:var(--solar)}
.stat .d{font-size:14px;color:var(--ink2)}
.panel{background:var(--panel);border-radius:14px;padding:24px}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:12px;border-bottom:1px solid var(--line);vertical-align:middle;color:var(--ink)}
td.num{text-align:right}
td small{display:block;color:var(--ink3);font-size:12px}
.pill{display:inline-block;padding:2px 10px;border-radius:999px;font-family:"Space Mono",monospace;font-size:10px;letter-spacing:.2em;text-transform:uppercase;white-space:nowrap}
.fix{color:var(--coral);border:1px solid var(--coral)}
.leverage{color:var(--lilac);border:1px solid var(--lilac)}
.hold{color:var(--ink3);border:1px solid var(--line)}
.split{display:flex;height:10px;border-radius:5px;overflow:hidden;background:var(--line);min-width:120px}
.split i{display:block;height:100%}
.split .l1{background:var(--magenta)}.split .l3{background:var(--purple)}
.legend{display:flex;flex-wrap:wrap;gap:16px;font-size:13px;color:var(--ink2)}
.legend span::before{content:"";display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px;background:var(--c)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
.card{background:var(--panel);border-radius:14px;padding:22px;display:grid;gap:10px;align-content:start}
.card p{font-size:15px}
ul.clean{margin:0;padding:0;list-style:none;display:grid;gap:12px}
ul.clean li{color:var(--ink2);max-width:72ch;padding-left:18px;position:relative}
ul.clean li::before{content:"";position:absolute;left:0;top:.7em;width:8px;height:2px;background:var(--coral)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{font-size:12px;padding:2px 8px;border-radius:6px;background:var(--panel2);color:var(--ink2);border:1px solid var(--line)}
.angle{display:grid;gap:8px;padding:16px 0;border-bottom:1px solid var(--line)}
.angle:last-child{border-bottom:0}
.angle .top{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:baseline}
.callout{border-left:2px solid var(--coral);padding:4px 0 4px 18px;color:var(--ink2);max-width:72ch}
.next{background:linear-gradient(135deg,rgba(75,46,131,.35),rgba(240,90,40,.18));border-radius:14px;padding:28px;display:grid;gap:10px}
.next .t{font-family:"Fraunces",Georgia,serif;font-size:clamp(22px,3vw,30px);color:var(--ink);line-height:1.25;max-width:40ch}
svg text{font-family:"Space Mono",monospace;font-size:11px;fill:var(--ink2)}
.foot{display:grid;gap:14px;border-top:1px solid var(--line);padding-top:28px}
.foot ol{margin:0;padding-left:18px;display:grid;gap:4px;font-size:13px;color:var(--ink3)}
.foot a{color:var(--ink2)}
.sig{display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:baseline}
.sig .wm{font-family:"Fraunces",Georgia,serif;font-style:italic;font-size:22px}
a{color:var(--pink)}
a:focus-visible{outline:2px solid var(--solar);outline-offset:2px}
.nav{display:flex;flex-wrap:wrap;gap:10px}
.nav a{font-family:"Space Mono",monospace;font-size:11px;letter-spacing:.2em;text-transform:uppercase;text-decoration:none;color:var(--ink2);border:1px solid var(--magenta);border-radius:999px;padding:6px 14px}
.meter{display:inline-block;width:64px;height:6px;border-radius:3px;background:var(--line);vertical-align:middle;margin-left:8px;overflow:hidden}
.meter i{display:block;height:100%;background:var(--purple)}
@media (max-width:640px){.mark{opacity:.35;width:80%}}
@media (prefers-reduced-motion:no-preference){.mark path{stroke-dasharray:1400;stroke-dashoffset:0;animation:draw 1.4s ease-out both}}
@keyframes draw{from{stroke-dashoffset:1400}to{stroke-dashoffset:0}}
"""

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,400;1,400&family=Outfit:wght@300;500;600&family=Space+Mono&display=swap">'

LATITUDE = ["#4B2E83", "#7B3FAB", "#C026A0", "#F05A28", "#F78DA7", "#FFCC00"]


def mark_svg():
    """Six sunrise-delta curves, violet (outer) to solar (inner)."""
    paths = []
    for k, col in enumerate(LATITUDE):
        amp = 150 - k * 22
        y0 = 250 - k * 6
        paths.append(
            f'<path d="M 20 {y0 + 60} C 160 {y0 + 40}, 260 {y0 - amp}, 400 {y0 - amp} '
            f'S 640 {y0 + 40}, 780 {y0 + 60}" stroke="{col}" style="animation-delay:{k * 0.12:.2f}s"/>'
        )
    return f'<svg class="mark" viewBox="0 0 800 340" aria-hidden="true">{"".join(paths)}</svg>'


def page(title, body):
    return f"<title>{e(title)}</title>\n{FONTS}\n<style>{CSS}</style>\n<div class=\"bar\"></div>\n<main class=\"wrap\">{body}</main>\n<div class=\"bar\"></div>\n"


def footer(sources, note):
    items = "".join(f'<li><a href="{u}">{e(t)}</a></li>' for t, u in sources)
    return f"""
<footer class="foot">
  <div class="label">Sources and method</div>
  <p style="font-size:14px">{note}</p>
  <ol>{items}</ol>
  <div class="sig"><span class="wm">jean-paul</span><span class="kicker">Where strategy meets sunrise</span></div>
  <p style="font-size:12px;color:var(--ink3)">Growth Grid framework and IP: Jean-Paul Edwards. Independent analysis; not affiliated with or endorsed by the brands shown.</p>
</footer>"""


METHOD_NOTE = (
    "Pilot v0.3, 24 Sep 2026. Market facts are sourced below; shares are Worldpanel figures as reported in the trade press. "
    "Intent importance is scored at category level and is identical for both brands. Delivery is analyst judgement anchored "
    "to the sources (inferred, medium confidence). Intent IDs are provisional until the canonical 47-intent taxonomy is loaded. "
    "Delegation priors are hypotheses to validate."
)


# ---------------------------------------------------------------- charts
def heat_chart(moments, lo=-30, hi=30, width=640, row=40):
    """Diverging bars: heat per Moment. Right (coral) = gap to fix, left (lilac) = strength."""
    left, right = 110, width - 16
    span = right - left

    def x(v):
        return left + (max(lo, min(hi, v)) - lo) / (hi - lo) * span

    h = row * len(moments) + 40
    out = [f'<svg viewBox="0 0 {width} {h}" width="100%" role="img" aria-label="Heat per Moment">']
    for t in range(lo, hi + 1, 10):
        out.append(f'<line x1="{x(t):.1f}" y1="8" x2="{x(t):.1f}" y2="{h - 26}" stroke="#262626" stroke-width="1"/>')
        out.append(f'<text x="{x(t):.1f}" y="{h - 8}" text-anchor="middle">{t:+d}</text>' if t else f'<text x="{x(t):.1f}" y="{h - 8}" text-anchor="middle">0</text>')
    for thr, lab in ((FIX_AT, "fix"), (LEVERAGE_AT, "leverage")):
        out.append(f'<line x1="{x(thr):.1f}" y1="8" x2="{x(thr):.1f}" y2="{h - 26}" stroke="#7A7A7A" stroke-dasharray="3 4"/>')
    for i, m in enumerate(moments):
        y = 14 + i * row
        v = m["heat"]
        col = "#F05A28" if v >= FIX_AT else ("#B08AE0" if v <= LEVERAGE_AT else "#7A7A7A")
        x0, x1 = sorted((x(0), x(v)))
        out.append(f'<text x="0" y="{y + 15}" style="text-transform:uppercase;letter-spacing:.15em">{m["moment"]}</text>')
        out.append(f'<rect x="{x0:.1f}" y="{y + 4}" width="{max(x1 - x0, 1.5):.1f}" height="16" rx="3" fill="{col}"/>')
        tx = x1 + 6 if v >= 0 else x0 - 6
        anchor = "start" if v >= 0 else "end"
        out.append(f'<text x="{tx:.1f}" y="{y + 16}" text-anchor="{anchor}" style="fill:#FFFFFF">{v:+.1f}</text>')
    out.append("</svg>")
    return "".join(out)


def grid_table(moments):
    rows = []
    for m in moments:
        di = m["delegation_index"]
        rows.append(f"""<tr>
<td><b style="font-weight:500">{m['moment'].capitalize()}</b><small>“{MOMENT_Q[m['moment']]}”</small></td>
<td class="num">{m['heat']:+.1f}</td>
<td><span class="pill {m['role']}">{m['role']}</span></td>
<td class="num">{di:.2f}<span class="meter"><i style="width:{di * 100:.0f}%"></i></span></td>
<td><div class="split" title="L1 {m['l1_creative_share']}% · L3 {m['l3_protocol_share']}%"><i class="l1" style="width:{m['l1_creative_share'] / (m['l1_creative_share'] + m['l3_protocol_share'] or 1) * 100:.0f}%"></i><i class="l3" style="flex:1"></i></div><small>{m['l1_creative_share']}% memory · {m['l3_protocol_share']}% protocol</small></td>
<td class="num">{m['angles']}{' <span class="pill fix">white space</span>' if m['white_space'] else ''}</td>
</tr>""")
    return f"""<div class="panel scroll"><table>
<thead><tr><th>Moment</th><th style="text-align:right">Heat</th><th>Role</th><th style="text-align:right">Delegation</th><th>Emphasis split</th><th style="text-align:right">Angles</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<div class="legend" style="margin-top:14px"><span style="--c:var(--magenta)">L1 memory share (people decide)</span><span style="--c:var(--purple)">L3 protocol share (agents decide)</span></div></div>"""


def intents_table(intents, n=5):
    mods = [i for i in intents if not i["modulator"]]
    gaps = sorted(mods, key=lambda i: -i["gap"])[:n]
    strengths = sorted(mods, key=lambda i: i["gap"])[:n]

    def rows(lst):
        return "".join(
            f'<tr><td>{e(i["name"])}<small>{i["taxonomy_id"]} · {i["primary_state"]}</small></td>'
            f'<td class="num">{i["importance"]}</td><td class="num">{i["delivery"]}</td>'
            f'<td class="num" style="color:{"var(--coral)" if i["gap"] > 0 else "var(--lilac)"}">{i["gap"]:+d}</td></tr>'
            for i in lst
        )

    head = '<thead><tr><th>Intent</th><th style="text-align:right">Importance</th><th style="text-align:right">Delivery</th><th style="text-align:right">Gap</th></tr></thead>'
    return f"""<div class="cards">
<div class="card scroll"><div class="label">Biggest gaps</div><table>{head}<tbody>{rows(gaps)}</tbody></table></div>
<div class="card scroll"><div class="label">Biggest strengths</div><table>{head}<tbody>{rows(strengths)}</tbody></table></div>
</div>"""


def agnt_table(intents):
    ag = [i for i in intents if i["domain"] == "AGNT"]
    rows = "".join(
        f'<tr><td>{e(i["name"])}<small>{i["taxonomy_id"]}</small></td><td class="num">{i["importance"]}</td><td class="num">{i["delivery"]}</td></tr>'
        for i in ag
    )
    return f'<table><thead><tr><th>Agentic intent (modulator)</th><th style="text-align:right">Importance</th><th style="text-align:right">Delivery</th></tr></thead><tbody>{rows}</tbody></table>'


def angles_block(angles):
    out = []
    for a in angles:
        chips = "".join(f'<span class="chip">{e(v)}</span>' for v in (a["mindset"], a["messaging"], a["proof"], a["context"]) if v)
        mom = a["moment"]
        out.append(f'<div class="angle"><div class="top"><h3>{e(a["name"])}</h3><span class="pill {"leverage" if mom == "CROSS" else "hold"}">{mom}</span></div><div class="chips">{chips}</div></div>')
    return "".join(out)


# ---------------------------------------------------------------- brand report
def brand_report(key):
    b = BRANDS[key]
    src, exp = load(key)
    ms = exp["moments"]
    gate = exp["agentic_gate"]
    take_val = f"{gate:.2f}" if b["takeaway_label"] == "Agentic Gate" else f"+{exp['need_state_heat']['replenish']:.1f}"
    stats = "".join(f'<div class="stat"><div class="n">{n}</div><div class="d">{e(d)}</div></div>' for n, d in b["stats"])
    stats += f'<div class="stat take"><div class="n">{take_val}</div><div class="d">{b["takeaway_label"]}: the number this report turns on</div></div>'
    other = "waitrose" if key == "lidl" else "lidl"
    layers = "".join(f'<div class="card"><div class="label">{e(k)}</div><h3>{e(t)}</h3><p>{e(d)}</p></div>' for k, t, d in b["layers"])
    measure = "".join(f"<tr><td class='mono' style='color:var(--ink)'>{k}</td><td>{e(v)}</td></tr>" for k, v in b["measure"])
    diag = "".join(f"<li>{d}</li>" for d in b["diagnosis"])
    body = f"""
<section class="hero">
  {mark_svg()}
  <div class="kicker">Growth Grid · UK grocery · Pilot v0.3</div>
  <h1>{b['title']}<br><span class="grad">get {b['gradient_word']}</span></h1>
  <p class="thesis">{e(b['thesis'])}</p>
  <nav class="nav"><a href="#grid">The grid</a><a href="#layers">What to do</a><a href="#angles">Creative</a><a href="#measure">Measurement</a></nav>
</section>

<section class="section"><div class="stats">{stats}</div></section>

<section class="section" id="grid">
  <header><div class="kicker">01 · The grid</div><h2>Where the gaps and strengths sit</h2>
  <p>Heat is the importance-weighted gap between what people need and what {b['title']} delivers in each Moment. Coral bars are gaps to fix. Lilac bars are strengths to lead the creative with.</p></header>
  <div class="panel">{heat_chart(ms)}</div>
  {grid_table(ms)}
  <p class="callout">Emphasis follows the size of each Moment in the category, split by who decides it. The shares describe where memory-building and agent-readiness work should go. They are not budget splits, and reach itself is never cut.</p>
</section>

<section class="section">
  <header><div class="kicker">02 · Diagnosis</div><h2>What the grid says</h2></header>
  <ul class="clean">{diag}</ul>
  {intents_table(exp['intents'])}
  <div class="cards"><div class="card scroll"><div class="label">Agentic Gate · {gate:.2f}</div>{agnt_table(exp['intents'])}
  <p style="font-size:14px">The gate is delivery over importance across these four intents. It scales how much of every Moment agents are modelled to decide.</p></div></div>
</section>

<section class="section" id="layers">
  <header><div class="kicker">03 · What to do, layer by layer</div><h2>Reach first, then the rest</h2></header>
  <div class="cards">{layers}</div>
</section>

<section class="section" id="angles">
  <header><div class="kicker">04 · Creative signal</div><h2>The Angle library</h2>
  <p>Moments reach the market through creative, never through audience targeting. Each Angle is a spine of mindset × messaging × proof × context. The platform's own model finds the people in that moment.</p></header>
  <div class="panel">{angles_block(exp['angles'])}</div>
  <p class="callout">{b['white_note']}</p>
</section>

<section class="section" id="measure">
  <header><div class="kicker">05 · Measurement</div><h2>Measure each layer on its own terms</h2></header>
  <div class="panel scroll"><table><tbody>{measure}</tbody></table></div>
</section>

<section class="next"><div class="kicker" style="color:var(--solar)">The one thing to do next</div><div class="t">{e(b['next'])}</div>
<p style="font-size:14px">{links(other)}</p></section>
{footer(b['sources'], METHOD_NOTE)}
"""
    return page(b["page_title"], body)


# ---------------------------------------------------------------- diagnostic report
def flip_sensitivity(src):
    """Smallest single delivery change that moves each Moment across its nearest role threshold."""
    res = {}
    for m in MOMENT_Q:
        members = [i for i in src["intents"] if i.get("moment") == m]
        w = sum(i["importance"] for i in members)
        heat = sum(i["importance"] * (i["importance"] - i["delivery"]) for i in members) / w
        role = "fix" if heat >= FIX_AT else ("leverage" if heat <= LEVERAGE_AT else "hold")
        if role == "fix":
            target = FIX_AT - 0.05  # raise delivery to fall below fix
        elif role == "leverage":
            target = LEVERAGE_AT + 0.05  # lower delivery to rise above leverage
        else:
            up, down = FIX_AT - heat, heat - LEVERAGE_AT
            target = FIX_AT if up <= down else LEVERAGE_AT
        best = None
        for i in members:
            delta = (heat - target) * w / i["importance"]  # delivery change needed
            new = i["delivery"] + delta
            if 1 <= new <= 100:
                if best is None or abs(delta) < abs(best[1]):
                    best = (i["name"], delta, i["delivery"])
        res[m] = (round(heat, 1), role, best)
    return res


def contributions(ls, ws, moment):
    """Per-intent contribution to Heat(Waitrose) − Heat(Lidl) for one Moment."""
    li = {i["taxonomy_id"]: i for i in ls["intents"]}
    members = [i for i in ws["intents"] if i.get("moment") == moment]
    w = sum(i["importance"] for i in members)
    return sorted(
        ((i["name"], i["importance"] * (li[i["taxonomy_id"]]["delivery"] - i["delivery"]) / w) for i in members),
        key=lambda t: -abs(t[1]),
    )


def diff_chart(lm, wm, width=640, row=46):
    """Paired dots: Lidl vs Waitrose heat per Moment on one scale."""
    lo, hi = -30, 30
    left, right = 110, width - 20

    def x(v):
        return left + (max(lo, min(hi, v)) - lo) / (hi - lo) * (right - left)

    h = row * len(lm) + 40
    out = [f'<svg viewBox="0 0 {width} {h}" width="100%" role="img" aria-label="Lidl vs Waitrose heat per Moment">']
    for t in range(lo, hi + 1, 10):
        out.append(f'<line x1="{x(t):.1f}" y1="8" x2="{x(t):.1f}" y2="{h - 26}" stroke="#262626"/>')
        out.append(f'<text x="{x(t):.1f}" y="{h - 8}" text-anchor="middle">{t:+d}</text>' if t else f'<text x="{x(t):.1f}" y="{h - 8}" text-anchor="middle">0</text>')
    for thr in (FIX_AT, LEVERAGE_AT):
        out.append(f'<line x1="{x(thr):.1f}" y1="8" x2="{x(thr):.1f}" y2="{h - 26}" stroke="#7A7A7A" stroke-dasharray="3 4"/>')
    for i, (a, b) in enumerate(zip(lm, wm)):
        y = 22 + i * row
        out.append(f'<text x="0" y="{y + 4}" style="text-transform:uppercase;letter-spacing:.15em">{a["moment"]}</text>')
        out.append(f'<line x1="{x(a["heat"]):.1f}" y1="{y}" x2="{x(b["heat"]):.1f}" y2="{y}" stroke="#7A7A7A" stroke-width="2"/>')
        out.append(f'<circle cx="{x(a["heat"]):.1f}" cy="{y}" r="7" fill="#F05A28"/>')
        out.append(f'<circle cx="{x(b["heat"]):.1f}" cy="{y}" r="7" fill="#7B3FAB" stroke="#B08AE0" stroke-width="2"/>')
    out.append("</svg>")
    return "".join(out)


def diagnostic_report():
    lsrc, lexp = load("lidl")
    wsrc, wexp = load("waitrose")
    lm, wm = lexp["moments"], wexp["moments"]

    rows = []
    for a, b in zip(lm, wm):
        c = contributions(lsrc, wsrc, a["moment"])
        top = c[0]
        rows.append(f"""<tr><td><b style="font-weight:500">{a['moment'].capitalize()}</b></td>
<td class="num">{a['heat']:+.1f} <span class="pill {a['role']}">{a['role']}</span></td>
<td class="num">{b['heat']:+.1f} <span class="pill {b['role']}">{b['role']}</span></td>
<td class="num">{b['heat'] - a['heat']:+.1f}</td>
<td>{e(top[0])}<small>contributes {top[1]:+.1f} of the difference</small></td></tr>""")

    sens_rows = []
    for brand, src in (("Lidl GB", lsrc), ("Waitrose", wsrc)):
        for m, (heat, role, best) in flip_sensitivity(src).items():
            if best is None:
                continue
            name, delta, cur = best
            new = cur + delta
            fragile = abs(delta) <= 15
            sens_rows.append(
                f"<tr><td>{brand}</td><td>{m.capitalize()}</td><td><span class='pill {role}'>{role}</span></td>"
                f"<td>{e(name)}</td><td class='num'>{cur} → {new:.0f}</td>"
                f"<td class='num' style='color:{'var(--coral)' if fragile else 'var(--ink2)'}'>{delta:+.0f}{' · fragile' if fragile else ''}</td></tr>"
            )

    ag_l = {i["taxonomy_id"]: i for i in lexp["intents"] if i["domain"] == "AGNT"}
    ag_rows = "".join(
        f"<tr><td>{e(i['name'])}</td><td class='num'>{i['importance']}</td><td class='num'>{ag_l[i['taxonomy_id']]['delivery']}</td><td class='num'>{i['delivery']}</td></tr>"
        for i in wexp["intents"] if i["domain"] == "AGNT"
    )

    levers = [
        ("Heat thresholds", f"fix ≥ {FIX_AT:+.0f}, leverage ≤ {LEVERAGE_AT:+.0f}", "Set which Moments are called gaps or strengths. Lidl Replenish sits only 3 points above the fix line."),
        ("Delegation priors", "Replenish 0.80 → Care 0.15", "Untested hypotheses. They set the shape of every L1/L3 split. Replace them with observed agent-referred share per Moment."),
        ("Uniform Agentic Gate", "one number per brand", "Scales every Moment equally, so L3 shares come out identical for both brands. A per-Moment gate would let agent readiness differ by Moment."),
        ("L1 floor", "0.15", "Minimum memory emphasis for a fully delegated Moment. Raise it if humans keep setting agent rules for longer."),
        ("Heat formula", "importance-weighted mean gap", "A provisional stand-in for your canonical crosswalk. Replace it once the crosswalk file is loaded."),
        ("Delivery scores", "analyst judgement", "The largest source of error. Run the evidence analyser on the fragile scores first."),
    ]
    lever_html = "".join(f'<div class="card"><div class="label">{e(k)}</div><h3>{e(v)}</h3><p>{e(d)}</p></div>' for k, v, d in levers)

    body = f"""
<section class="hero">
  {mark_svg()}
  <div class="kicker">Growth Grid · Diagnostic · Lidl GB vs Waitrose</div>
  <h1>Same category,<br><span class="grad">opposite</span> failure modes</h1>
  <p class="thesis">Both brands' hottest Moment is one agents will take first. Lidl lacks eligibility; Waitrose lacks justification. This page shows why the model produced that, and which settings we can tune.</p>
  <nav class="nav"><a href="#why">Why they differ</a><a href="#gate">The gate</a><a href="#fragile">Fragile calls</a><a href="#levers">Levers</a>{brand_links()}</nav>
</section>

<section class="section">
  <div class="stats">
    <div class="stat"><div class="n">0</div><div class="d">Importance scores that differ between the brands, so every difference comes from delivery</div></div>
    <div class="stat"><div class="n">{lexp['agentic_gate']:.2f} / {wexp['agentic_gate']:.2f}</div><div class="d">Agentic Gate, Lidl / Waitrose</div></div>
    <div class="stat take"><div class="n">Eligible vs justified</div><div class="d">The two different L3 jobs the same grid prescribes</div></div>
  </div>
</section>

<section class="section" id="why">
  <header><div class="kicker">01 · Why the outputs differ</div><h2>Heat, side by side</h2>
  <p>Coral dots are Lidl, purple dots are Waitrose. Dashed lines mark the fix (+5) and leverage (−10) thresholds. The table names the single intent that contributes most to the gap between the two brands in each Moment.</p></header>
  <div class="panel">{diff_chart(lm, wm)}
  <div class="legend" style="margin-top:10px"><span style="--c:var(--coral)">Lidl GB</span><span style="--c:var(--purple)">Waitrose</span></div></div>
  <div class="panel scroll"><table><thead><tr><th>Moment</th><th style="text-align:right">Lidl</th><th style="text-align:right">Waitrose</th><th style="text-align:right">Δ (W − L)</th><th>Biggest driver</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
  <ul class="clean">
    <li><b>Replenish</b> is hot for both brands, for different reasons. Waitrose's Budget fit gap (+45) outweighs Lidl's range and availability gaps.</li>
    <li><b>Plan</b> splits them: Lidl has no planning or basket help (cognitive offload 30 vs 60), and in-store-only shopping makes time pressure worse.</li>
    <li><b>Celebrate and Care</b> are where Waitrose pulls away: self-reward, occasion fit, provenance and authenticity all over-deliver by 20–35 points.</li>
  </ul>
</section>

<section class="section" id="gate">
  <header><div class="kicker">02 · The Agentic Gate</div><h2>Why agents see the brands differently</h2>
  <p>The gate is delivery over importance across the agentic intents. It multiplies each Moment's delegation prior, so it decides how much of the grid agents are modelled to decide.</p></header>
  <div class="cards">
    <div class="card scroll"><table><thead><tr><th>Agentic intent</th><th style="text-align:right">Imp.</th><th style="text-align:right">Lidl</th><th style="text-align:right">Waitrose</th></tr></thead><tbody>{ag_rows}</tbody>
    <tfoot><tr><td class="mono">Gate</td><td></td><td class="num">{lexp['agentic_gate']:.2f}</td><td class="num">{wexp['agentic_gate']:.2f}</td></tr></tfoot></table></div>
    <div class="card"><div class="label">What follows</div>
    <p>System compatibility (10 vs 30) and delegation confidence (15 vs 35) drive most of the difference. Lidl has no online grocery for an agent to act on; Waitrose runs ~160k deliveries a week.</p>
    <p>Consequence: Waitrose's Replenish is modelled as 75% agent-decided vs Lidl's 41%. Waitrose's price gap is more exposed to machine comparison than Lidl's planning gap is.</p></div>
  </div>
</section>

<section class="section" id="fragile">
  <header><div class="kicker">03 · How fragile each call is</div><h2>The smallest change that flips a role</h2>
  <p>For each Moment, the single delivery score that would move it across the nearest threshold with the smallest change. A shift of 15 points or less is flagged as fragile; those scores need evidence first.</p></header>
  <div class="panel scroll"><table><thead><tr><th>Brand</th><th>Moment</th><th>Role</th><th>Easiest score to move</th><th style="text-align:right">Delivery now → flip</th><th style="text-align:right">Change</th></tr></thead><tbody>{''.join(sens_rows)}</tbody></table></div>
  <p class="callout">The headline rests on Waitrose Replenish and Lidl Plan. Waitrose's Budget fit would have to rise by about 32 points to lose its fix role, so that call is robust. Lidl's Plan fix needs a 17-point move, so it is moderately robust. Lidl's Replenish fix is the weakest call on the page: Budget fit rising from 88 to 98 would drop it to hold.</p>
</section>

<section class="section" id="levers">
  <header><div class="kicker">04 · Levers we can tune together</div><h2>Model settings, and what each one changes</h2></header>
  <div class="cards">{lever_html}</div>
</section>

<section class="section">
  <header><div class="kicker">05 · What the pilot changed in the framework</div><h2>Three lessons, already applied</h2></header>
  <ul class="clean">
    <li><b>Formula fix (v0.2 → v0.3).</b> Weighting memory emphasis by gap starved Waitrose's strengths to about 1.6%, which breaks the rule that memory is built across every entry point. Emphasis now follows each Moment's size in the category; heat only sets the role.</li>
    <li><b>Vocabulary gap.</b> The creative-signal Messaging pillar has no value for provenance or standards, so Waitrose's biggest asset could not be expressed. The spine check caught it as a clash. Logged as a candidate pillar revision.</li>
    <li><b>Provisional taxonomy.</b> Intent IDs carry a -P suffix until the canonical 47-intent taxonomy and crosswalk are loaded.</li>
  </ul>
</section>

<section class="next"><div class="kicker" style="color:var(--solar)">The one thing to do next</div>
<div class="t">Evidence the fragile scores first (Lidl's Budget fit and taste, Waitrose's cost-of-living and time scores, and the four agentic intents), then re-run both grids.</div></section>
{footer(BRANDS['lidl']['sources'][:2] + BRANDS['waitrose']['sources'][1:2] + BRANDS['waitrose']['sources'][3:], METHOD_NOTE)}
"""
    return page("Lidl vs Waitrose Diagnostic", body)


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "lidl-growth-grid.html").write_text(brand_report("lidl"))
    (OUT / "waitrose-growth-grid.html").write_text(brand_report("waitrose"))
    (OUT / "lidl-vs-waitrose-diagnostic.html").write_text(diagnostic_report())
    print(f"wrote {len(list(OUT.glob('*.html')))} reports to {OUT}")


if __name__ == "__main__":
    main()
