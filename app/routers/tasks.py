from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Plan, Task, TaskStatus
from app.services.intent_service import auto_update_intent_status
from app.services.task_service import (
    add_dependency,
    calculate_plan_progress,
    remove_dependency,
    update_task_status,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/plans/{plan_id}/tasks/new", response_class=HTMLResponse)
def new_task_form(request: Request, plan_id: int):
    return templates.TemplateResponse(
        "partials/task_form.html", {"request": request, "plan_id": plan_id}
    )


@router.post("/plans/{plan_id}/tasks", response_class=HTMLResponse)
def create_task(
    request: Request,
    plan_id: int,
    title: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    plan = db.query(Plan).get(plan_id)
    if not plan:
        return HTMLResponse("<p>Plan not found</p>", status_code=404)

    max_order = max((t.order for t in plan.tasks), default=-1)
    task = Task(
        plan_id=plan_id,
        title=title,
        description=description or None,
        order=max_order + 1,
    )
    db.add(task)
    db.commit()
    db.refresh(plan)
    progress = calculate_plan_progress(db, plan_id)
    return templates.TemplateResponse(
        "partials/task_list.html",
        {"request": request, "plan": plan, "progress": progress},
    )


@router.patch("/tasks/{task_id}/status", response_class=HTMLResponse)
def change_task_status(
    request: Request,
    task_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        task = update_task_status(db, task_id, TaskStatus(status))
    except ValueError as e:
        return HTMLResponse(f'<div class="error-toast" role="alert">{e}</div>', status_code=422)

    plan = task.plan
    progress = calculate_plan_progress(db, plan.id)

    # Auto-update intent status
    auto_update_intent_status(db, plan.intent_id)

    # Return task row + OOB progress bar
    task_html = templates.TemplateResponse(
        "partials/task_row.html",
        {"request": request, "task": task, "plan": plan},
    ).body.decode()

    progress_html = templates.TemplateResponse(
        "partials/progress_bar.html",
        {"request": request, "progress": progress, "plan_id": plan.id},
    ).body.decode()

    return HTMLResponse(task_html + progress_html)


@router.delete("/tasks/{task_id}", response_class=HTMLResponse)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).get(task_id)
    if task:
        db.delete(task)
        db.commit()
    return HTMLResponse("")


@router.post("/tasks/{task_id}/dependencies", response_class=HTMLResponse)
def add_task_dependency(
    request: Request,
    task_id: int,
    depends_on_id: int = Form(...),
    db: Session = Depends(get_db),
):
    try:
        add_dependency(db, task_id, depends_on_id)
    except ValueError as e:
        return HTMLResponse(f'<div class="error-toast" role="alert">{e}</div>', status_code=422)

    task = db.query(Task).get(task_id)
    plan = task.plan
    progress = calculate_plan_progress(db, plan.id)
    return templates.TemplateResponse(
        "partials/task_list.html",
        {"request": request, "plan": plan, "progress": progress},
    )


@router.delete("/tasks/{task_id}/dependencies/{dep_id}", response_class=HTMLResponse)
def remove_task_dependency(
    request: Request,
    task_id: int,
    dep_id: int,
    db: Session = Depends(get_db),
):
    try:
        remove_dependency(db, task_id, dep_id)
    except ValueError as e:
        return HTMLResponse(f'<div class="error-toast" role="alert">{e}</div>', status_code=422)

    task = db.query(Task).get(task_id)
    plan = task.plan
    progress = calculate_plan_progress(db, plan.id)
    return templates.TemplateResponse(
        "partials/task_list.html",
        {"request": request, "plan": plan, "progress": progress},
    )
