from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Intent, IntentStatus
from app.services.task_service import calculate_intent_progress

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    intents = db.query(Intent).order_by(Intent.updated_at.desc()).all()
    progress_map = {}
    for intent in intents:
        progress_map[intent.id] = calculate_intent_progress(db, intent.id)
    return templates.TemplateResponse(
        request,
        "index.html",
        {"request": request, "intents": intents, "progress_map": progress_map},
    )


@router.get("/intents/new", response_class=HTMLResponse)
def new_intent_form(request: Request):
    return templates.TemplateResponse(
        request,
        "partials/intent_form.html", {"request": request}
    )


@router.post("/intents", response_class=HTMLResponse)
def create_intent(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    intent = Intent(title=title, description=description or None)
    db.add(intent)
    db.commit()
    db.refresh(intent)
    intents = db.query(Intent).order_by(Intent.updated_at.desc()).all()
    progress_map = {}
    for i in intents:
        progress_map[i.id] = calculate_intent_progress(db, i.id)
    return templates.TemplateResponse(
        request,
        "partials/intent_list.html",
        {"request": request, "intents": intents, "progress_map": progress_map},
    )


@router.get("/intents/{intent_id}", response_class=HTMLResponse)
def intent_detail(request: Request, intent_id: int, db: Session = Depends(get_db)):
    intent = db.query(Intent).get(intent_id)
    if not intent:
        return HTMLResponse("<p>Intent not found</p>", status_code=404)
    progress = calculate_intent_progress(db, intent_id)
    return templates.TemplateResponse(
        request,
        "intent_detail.html",
        {"request": request, "intent": intent, "progress": progress},
    )


@router.put("/intents/{intent_id}", response_class=HTMLResponse)
def update_intent(
    request: Request,
    intent_id: int,
    title: str = Form(None),
    description: str = Form(None),
    status: str = Form(None),
    db: Session = Depends(get_db),
):
    intent = db.query(Intent).get(intent_id)
    if not intent:
        return HTMLResponse("<p>Intent not found</p>", status_code=404)
    if title:
        intent.title = title
    if description is not None:
        intent.description = description or None
    if status:
        intent.status = IntentStatus(status)
    db.commit()
    db.refresh(intent)
    progress = calculate_intent_progress(db, intent_id)
    return templates.TemplateResponse(
        request,
        "intent_detail.html",
        {"request": request, "intent": intent, "progress": progress},
    )


@router.delete("/intents/{intent_id}", response_class=HTMLResponse)
def delete_intent(intent_id: int, db: Session = Depends(get_db)):
    intent = db.query(Intent).get(intent_id)
    if intent:
        db.delete(intent)
        db.commit()
    return HTMLResponse("")
