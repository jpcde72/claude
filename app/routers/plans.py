from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Intent, Plan
from app.services.task_service import calculate_intent_progress, calculate_plan_progress

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/intents/{intent_id}/plans/new", response_class=HTMLResponse)
def new_plan_form(request: Request, intent_id: int):
    return templates.TemplateResponse(
        request,
        "partials/plan_form.html", {"request": request, "intent_id": intent_id}
    )


@router.post("/intents/{intent_id}/plans", response_class=HTMLResponse)
def create_plan(
    request: Request,
    intent_id: int,
    title: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    intent = db.query(Intent).get(intent_id)
    if not intent:
        return HTMLResponse("<p>Intent not found</p>", status_code=404)

    max_order = max((p.order for p in intent.plans), default=-1)
    plan = Plan(
        intent_id=intent_id,
        title=title,
        description=description or None,
        order=max_order + 1,
    )
    db.add(plan)
    db.commit()
    db.refresh(intent)
    progress = calculate_intent_progress(db, intent_id)
    return templates.TemplateResponse(
        request,
        "partials/plan_list.html",
        {"request": request, "intent": intent, "progress": progress},
    )


@router.get("/plans/{plan_id}", response_class=HTMLResponse)
def plan_detail(request: Request, plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(Plan).get(plan_id)
    if not plan:
        return HTMLResponse("<p>Plan not found</p>", status_code=404)
    progress = calculate_plan_progress(db, plan_id)
    return templates.TemplateResponse(
        request,
        "plan_detail.html",
        {"request": request, "plan": plan, "progress": progress},
    )


@router.put("/plans/{plan_id}", response_class=HTMLResponse)
def update_plan(
    request: Request,
    plan_id: int,
    title: str = Form(None),
    description: str = Form(None),
    db: Session = Depends(get_db),
):
    plan = db.query(Plan).get(plan_id)
    if not plan:
        return HTMLResponse("<p>Plan not found</p>", status_code=404)
    if title:
        plan.title = title
    if description is not None:
        plan.description = description or None
    db.commit()
    db.refresh(plan)
    progress = calculate_plan_progress(db, plan_id)
    return templates.TemplateResponse(
        request,
        "plan_detail.html",
        {"request": request, "plan": plan, "progress": progress},
    )


@router.delete("/plans/{plan_id}", response_class=HTMLResponse)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(Plan).get(plan_id)
    if plan:
        db.delete(plan)
        db.commit()
    return HTMLResponse("")
