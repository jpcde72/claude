from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Angle, Grid, IntentDomain, IntentScore, Moment, MomentSetting
from app.services.grid_service import create_grid, export_json, summarise

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _moment_or_none(value: str) -> Moment | None:
    return Moment(value) if value else None


def _clamp_score(value: int) -> int:
    return max(1, min(100, value))


def _render_grid(request: Request, grid: Grid, template: str = "grid_detail.html"):
    return templates.TemplateResponse(
        request,
        template,
        context={
            "grid": grid,
            "summary": summarise(grid),
            "moments": list(Moment),
            "domains": list(IntentDomain),
        },
    )


@router.get("/grids", response_class=HTMLResponse)
def grid_index(request: Request, db: Session = Depends(get_db)):
    grids = db.query(Grid).order_by(Grid.updated_at.desc()).all()
    return templates.TemplateResponse(request, "grids.html", context={"grids": grids})


@router.post("/grids", response_class=HTMLResponse)
def grid_create(
    request: Request,
    brand: str = Form(...),
    market: str = Form(...),
    category: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    create_grid(db, brand, market, category, notes or None)
    grids = db.query(Grid).order_by(Grid.updated_at.desc()).all()
    return templates.TemplateResponse(
        request, "partials/grid_list.html", context={"grids": grids}
    )


@router.get("/grids/{grid_id}", response_class=HTMLResponse)
def grid_detail(request: Request, grid_id: int, db: Session = Depends(get_db)):
    grid = db.get(Grid, grid_id)
    if not grid:
        return HTMLResponse("<p>Grid not found</p>", status_code=404)
    return _render_grid(request, grid)


@router.get("/grids/{grid_id}/export.json")
def grid_export(grid_id: int, db: Session = Depends(get_db)):
    grid = db.get(Grid, grid_id)
    if not grid:
        return JSONResponse({"detail": "Grid not found"}, status_code=404)
    return JSONResponse(export_json(grid))


@router.delete("/grids/{grid_id}", response_class=HTMLResponse)
def grid_delete(grid_id: int, db: Session = Depends(get_db)):
    grid = db.get(Grid, grid_id)
    if grid:
        db.delete(grid)
        db.commit()
    return HTMLResponse("")


@router.post("/grids/{grid_id}/intents", response_class=HTMLResponse)
def intent_score_create(
    request: Request,
    grid_id: int,
    taxonomy_id: str = Form(...),
    name: str = Form(...),
    domain: str = Form(...),
    moment: str = Form(""),
    importance: int = Form(...),
    delivery: int = Form(...),
    db: Session = Depends(get_db),
):
    grid = db.get(Grid, grid_id)
    if not grid:
        return HTMLResponse("<p>Grid not found</p>", status_code=404)
    grid.intent_scores.append(
        IntentScore(
            taxonomy_id=taxonomy_id.strip().upper(),
            name=name,
            domain=IntentDomain(domain),
            moment=_moment_or_none(moment),
            importance=_clamp_score(importance),
            delivery=_clamp_score(delivery),
        )
    )
    db.commit()
    db.refresh(grid)
    return _render_grid(request, grid, "partials/grid_body.html")


@router.delete("/grid-intents/{score_id}", response_class=HTMLResponse)
def intent_score_delete(request: Request, score_id: int, db: Session = Depends(get_db)):
    score = db.get(IntentScore, score_id)
    if not score:
        return HTMLResponse("", status_code=404)
    grid = score.grid
    db.delete(score)
    db.commit()
    db.refresh(grid)
    return _render_grid(request, grid, "partials/grid_body.html")


@router.post("/grids/{grid_id}/angles", response_class=HTMLResponse)
def angle_create(
    request: Request,
    grid_id: int,
    name: str = Form(...),
    moment: str = Form(""),
    mindset: str = Form(...),
    messaging: str = Form(...),
    proof: str = Form(""),
    context: str = Form(""),
    db: Session = Depends(get_db),
):
    grid = db.get(Grid, grid_id)
    if not grid:
        return HTMLResponse("<p>Grid not found</p>", status_code=404)
    grid.angles.append(
        Angle(
            name=name,
            moment=_moment_or_none(moment),
            mindset=mindset,
            messaging=messaging,
            proof=proof or None,
            context=context or None,
        )
    )
    db.commit()
    db.refresh(grid)
    return _render_grid(request, grid, "partials/grid_body.html")


@router.delete("/angles/{angle_id}", response_class=HTMLResponse)
def angle_delete(request: Request, angle_id: int, db: Session = Depends(get_db)):
    angle = db.get(Angle, angle_id)
    if not angle:
        return HTMLResponse("", status_code=404)
    grid = angle.grid
    db.delete(angle)
    db.commit()
    db.refresh(grid)
    return _render_grid(request, grid, "partials/grid_body.html")


@router.put("/grids/{grid_id}/priors", response_class=HTMLResponse)
async def priors_update(request: Request, grid_id: int, db: Session = Depends(get_db)):
    grid = db.get(Grid, grid_id)
    if not grid:
        return HTMLResponse("<p>Grid not found</p>", status_code=404)
    form = await request.form()
    settings = {s.moment: s for s in grid.moment_settings}
    for m in Moment:
        raw = form.get(f"prior_{m.value}")
        if raw in (None, ""):
            continue
        value = max(0.0, min(1.0, float(raw)))
        if m in settings:
            settings[m].delegation_prior = value
        else:
            grid.moment_settings.append(MomentSetting(moment=m, delegation_prior=value))
    db.commit()
    db.refresh(grid)
    return _render_grid(request, grid, "partials/grid_body.html")
