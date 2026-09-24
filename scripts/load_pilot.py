"""Load pilot definitions into the app database and write their JSON exports.

Usage: python scripts/load_pilot.py pilots/lidl_uk.json [more.json ...]
"""

import json
import sys
from pathlib import Path

from app.database import SessionLocal, init_db
from app.services.grid_service import export_json, import_grid


def main(paths: list[str]) -> None:
    init_db()
    db = SessionLocal()
    try:
        for path in paths:
            grid = import_grid(db, json.loads(Path(path).read_text()))
            out = Path(path).with_name(Path(path).stem + ".export.json")
            out.write_text(json.dumps(export_json(grid), indent=2) + "\n")
            print(f"grid {grid.id}: {grid.brand} {grid.market} -> {out}")
    finally:
        db.close()


if __name__ == "__main__":
    main(sys.argv[1:])
