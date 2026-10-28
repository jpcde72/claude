# Intent Planner

FastAPI + HTMX app: an Intent has Plans, a Plan has Tasks, Tasks can depend on other Tasks.

## Commands
- Install: `pip install -e ".[dev]"`
- Run: `fastapi dev app/main.py`
- Test: `pytest` (none written yet)
- Lint: `ruff check .`

## Layout
- `app/models.py`: SQLAlchemy 2.0 models (Intent, Plan, Task, `task_dependencies`) and status enums
- `app/routers/`: one router per resource; return HTML fragments for HTMX, not JSON
- `app/services/`: business logic (e.g. progress calculation), called by routers
- `app/templates/`: full pages plus `partials/` swapped in by HTMX
- `app/config.py`: settings from env vars prefixed `INTENT_PLANNER_` (default DB: SQLite `intent_planner.db`)

## Conventions
- Keep logic in `services/`, routers thin.
- `TemplateResponse` takes `request` first (Starlette 1.x API).
- Tables are created on startup via `init_db()`; there are no migrations.
