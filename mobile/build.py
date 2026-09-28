"""Build the phone version of GEO Studio (a claude.ai artifact) from the canonical knowledge model.

    python mobile/build.py   ->  mobile/geo-studio.html

Edit skills/geo-axo-strategist/assets/knowledge.json, rebuild, then republish the artifact.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "mobile" / "geo_studio.template.html"
KNOWLEDGE = ROOT / "skills" / "geo-axo-strategist" / "assets" / "knowledge.json"
OUT = ROOT / "mobile" / "geo-studio.html"
PLACEHOLDER = "/*__KNOWLEDGE__*/null"


def main() -> None:
    kb = json.loads(KNOWLEDGE.read_text(encoding="utf-8"))
    # "</" would close the inline <script>; escape it inside the JSON literal.
    payload = json.dumps(kb, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8")
    if PLACEHOLDER not in html:
        raise SystemExit("placeholder missing from template")
    OUT.write_text(html.replace(PLACEHOLDER, payload), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
