import json
import re
from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.models_geo import ASSET_KINDS, Asset, AssetVersion, BrandProject, LLMExchange
from app.services import geo_llm
from app.services.geo_knowledge import (
    ari_band,
    ari_score,
    load_doc,
    load_knowledge,
    render_markdown,
)

router = APIRouter(prefix="/geo")
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["md"] = render_markdown
templates.env.globals.update(ari_score=ari_score, ari_band=ari_band, ASSET_KINDS=ASSET_KINDS)

SEGMENTS = ("consumer", "b2b", "both")


def _render(request: Request, name: str, **context):
    brand = request.cookies.get("geo_brand", "jp")
    context.update(brand=brand if brand in ("jp", "om") else "jp", kb=load_knowledge())
    return templates.TemplateResponse(request, name, context=context)


def _project_or_404(db: Session, project_id: int) -> BrandProject:
    project = db.get(BrandProject, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    return project


def _asset_or_404(db: Session, asset_id: int) -> Asset:
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(404, "Asset not found")
    return asset


def _add_version(db: Session, asset: Asset, content: str, source: str, note: str | None) -> AssetVersion:
    next_version = (asset.current.version + 1) if asset.current else 1
    version = AssetVersion(
        asset_id=asset.id, version=next_version, content=content, source=source, change_note=note or None
    )
    db.add(version)
    asset.updated_at = datetime.utcnow()
    db.flush()
    db.refresh(asset)
    return version


# ---------------------------------------------------------------- pages


@router.get("", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    projects = db.query(BrandProject).order_by(BrandProject.updated_at.desc()).all()
    recent = db.query(LLMExchange).order_by(LLMExchange.created_at.desc()).limit(6).all()
    return _render(request, "geo/dashboard.html", section="dash", projects=projects, recent=recent)


@router.get("/knowledge", response_class=HTMLResponse)
def knowledge(request: Request, db: Session = Depends(get_db)):
    projects = db.query(BrandProject).order_by(BrandProject.name).all()
    return _render(request, "geo/knowledge.html", section="kb", projects=projects)


@router.get("/knowledge/{doc}", response_class=HTMLResponse)
def knowledge_doc(doc: str, request: Request, db: Session = Depends(get_db)):
    if doc not in ("outlook", "playbook"):
        raise HTTPException(404)
    projects = db.query(BrandProject).order_by(BrandProject.name).all()
    titles = {"outlook": "2027 outlook", "playbook": "Playbook"}
    return _render(request, "geo/doc.html", section=doc, doc=load_doc(doc), title=titles[doc], projects=projects)


@router.get("/knowledge.json")
def knowledge_json():
    return load_knowledge()


# ---------------------------------------------------------------- projects


@router.post("/projects")
def create_project(
    name: str = Form(...),
    sector: str = Form(""),
    market: str = Form(""),
    segment: str = Form("consumer"),
    website: str = Form(""),
    competitors: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    project = BrandProject(
        name=name.strip(),
        sector=sector.strip() or None,
        market=market.strip() or None,
        segment=segment if segment in SEGMENTS else "consumer",
        website=website.strip() or None,
        competitors=competitors.strip() or None,
        notes=notes.strip() or None,
    )
    db.add(project)
    db.commit()
    return RedirectResponse(f"/geo/projects/{project.id}", status_code=303)


@router.get("/projects/{project_id}", response_class=HTMLResponse)
def project_detail(project_id: int, request: Request, db: Session = Depends(get_db)):
    project = _project_or_404(db, project_id)
    projects = db.query(BrandProject).order_by(BrandProject.name).all()
    return _render(request, "geo/project.html", section="dash", project=project, projects=projects)


@router.post("/projects/{project_id}")
def update_project(
    project_id: int,
    name: str = Form(...),
    sector: str = Form(""),
    market: str = Form(""),
    segment: str = Form("consumer"),
    website: str = Form(""),
    competitors: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    project = _project_or_404(db, project_id)
    project.name = name.strip()
    project.sector = sector.strip() or None
    project.market = market.strip() or None
    project.segment = segment if segment in SEGMENTS else project.segment
    project.website = website.strip() or None
    project.competitors = competitors.strip() or None
    project.notes = notes.strip() or None
    db.commit()
    return RedirectResponse(f"/geo/projects/{project.id}", status_code=303)


@router.get("/projects/{project_id}/assets.json")
def project_assets_json(project_id: int, db: Session = Depends(get_db)):
    project = _project_or_404(db, project_id)
    return [
        {"id": a.id, "title": a.title, "kind": a.kind, "version": a.current.version if a.current else 0}
        for a in project.assets
    ]


@router.post("/projects/{project_id}/delete")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db.delete(_project_or_404(db, project_id))
    db.commit()
    return RedirectResponse("/geo", status_code=303)


@router.post("/projects/{project_id}/ari")
async def save_ari(project_id: int, request: Request, db: Session = Depends(get_db)):
    project = _project_or_404(db, project_id)
    form = await request.form()
    scores = {}
    for c in load_knowledge()["ari"]["components"]:
        raw = form.get(c["id"])
        if raw not in (None, ""):
            scores[c["id"]] = max(0, min(100, int(raw)))
    project.ari_json = json.dumps(scores)
    db.commit()
    return RedirectResponse(f"/geo/projects/{project.id}#ari", status_code=303)


@router.get("/projects/{project_id}/export.md", response_class=PlainTextResponse)
def export_project(project_id: int, db: Session = Depends(get_db)):
    p = _project_or_404(db, project_id)
    parts = [f"# {p.name}", f"{p.sector or ''} · {p.market or ''} · {p.segment}".strip(" ·"), ""]
    score = ari_score(p.ari)
    if score is not None:
        parts += [f"**Agent Readiness Index v2:** {score} ({ari_band(score)})", ""]
    for a in p.assets:
        if a.current:
            parts += [f"## {a.title}", f"*{a.kind_label} · v{a.current.version}*", "", a.current.content, ""]
    slug = re.sub(r"[^a-z0-9]+", "-", p.name.lower()).strip("-") or "project"
    return PlainTextResponse(
        "\n".join(parts), headers={"Content-Disposition": f'attachment; filename="{slug}-geo.md"'}
    )


# ---------------------------------------------------------------- assets


@router.post("/projects/{project_id}/assets")
def create_asset(
    project_id: int,
    title: str = Form(...),
    kind: str = Form("note"),
    content: str = Form(""),
    tags: str = Form(""),
    db: Session = Depends(get_db),
):
    project = _project_or_404(db, project_id)
    asset = Asset(
        project_id=project.id,
        title=title.strip(),
        kind=kind if kind in ASSET_KINDS else "note",
        tags=tags.strip() or None,
    )
    db.add(asset)
    db.flush()
    _add_version(db, asset, content, "manual", "Created")
    project.updated_at = asset.updated_at
    db.commit()
    return RedirectResponse(f"/geo/assets/{asset.id}", status_code=303)


@router.get("/assets/{asset_id}", response_class=HTMLResponse)
def asset_detail(asset_id: int, request: Request, v: int | None = None, db: Session = Depends(get_db)):
    asset = _asset_or_404(db, asset_id)
    shown = next((x for x in asset.versions if x.version == v), None) if v else asset.current
    projects = db.query(BrandProject).order_by(BrandProject.name).all()
    return _render(request, "geo/asset.html", section="dash", asset=asset, shown=shown, project=asset.project, projects=projects)


@router.post("/assets/{asset_id}/versions")
def add_asset_version(
    asset_id: int,
    content: str = Form(...),
    title: str = Form(""),
    kind: str = Form(""),
    tags: str = Form(""),
    change_note: str = Form(""),
    db: Session = Depends(get_db),
):
    asset = _asset_or_404(db, asset_id)
    if title.strip():
        asset.title = title.strip()
    if kind in ASSET_KINDS:
        asset.kind = kind
    asset.tags = tags.strip() or None
    _add_version(db, asset, content, "manual", change_note)
    db.commit()
    return RedirectResponse(f"/geo/assets/{asset.id}", status_code=303)


@router.post("/assets/{asset_id}/restore/{version}")
def restore_version(asset_id: int, version: int, db: Session = Depends(get_db)):
    asset = _asset_or_404(db, asset_id)
    old = next((x for x in asset.versions if x.version == version), None)
    if old is None:
        raise HTTPException(404, "Version not found")
    _add_version(db, asset, old.content, "restore", f"Restored v{version}")
    db.commit()
    return RedirectResponse(f"/geo/assets/{asset.id}", status_code=303)


@router.post("/assets/{asset_id}/delete")
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = _asset_or_404(db, asset_id)
    project_id = asset.project_id
    db.delete(asset)
    db.commit()
    return RedirectResponse(f"/geo/projects/{project_id}", status_code=303)


# ---------------------------------------------------------------- live Claude


class AskBody(BaseModel):
    question: str
    project_id: int | None = None
    asset_ids: list[int] = []
    history_ids: list[int] = []
    web_search: bool = True


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


@router.post("/ask")
async def ask(body: AskBody):
    question = body.question.strip()
    if not question:
        raise HTTPException(422, "Question is empty")

    # Load everything up front: the stream outlives a request-scoped session.
    db = SessionLocal()
    try:
        project = db.get(BrandProject, body.project_id) if body.project_id else None
        assets = [a for a in (db.get(Asset, i) for i in body.asset_ids[:8]) if a and project and a.project_id == project.id]
        history = [h for h in (db.get(LLMExchange, i) for i in body.history_ids[-6:]) if h]
        req = geo_llm.AskRequest(question, project, assets, history, body.web_search)
        geo_llm.project_context(req)  # touches every lazy attribute so they load before close
    finally:
        db.close()

    async def events():
        async for event in geo_llm.stream_answer(req):
            if event["type"] == "final":
                with SessionLocal() as s:
                    ex = LLMExchange(
                        project_id=body.project_id if project else None,
                        question=question,
                        answer=event["answer"],
                        model=event["model"],
                        web_search=body.web_search,
                    )
                    s.add(ex)
                    s.commit()
                    yield _sse({"type": "done", "exchange_id": ex.id})
            else:
                yield _sse(event)

    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


@router.post("/exchanges/{exchange_id}/save")
def save_exchange(
    exchange_id: int,
    project_id: int = Form(...),
    title: str = Form(""),
    kind: str = Form("llm_answer"),
    asset_id: int | None = Form(None),
    db: Session = Depends(get_db),
):
    ex = db.get(LLMExchange, exchange_id)
    if ex is None:
        raise HTTPException(404, "Exchange not found")
    project = _project_or_404(db, project_id)
    if asset_id:
        asset = _asset_or_404(db, asset_id)
        if asset.project_id != project.id:
            raise HTTPException(400, "Asset belongs to another project")
        _add_version(db, asset, ex.answer, "claude", f"Updated by Claude: {ex.question[:120]}")
    else:
        asset = Asset(
            project_id=project.id,
            title=(title.strip() or ex.question[:120]),
            kind=kind if kind in ASSET_KINDS else "llm_answer",
        )
        db.add(asset)
        db.flush()
        _add_version(db, asset, ex.answer, "claude", f"From question: {ex.question[:120]}")
    ex.project_id = project.id
    db.commit()
    return {"asset_id": asset.id, "url": f"/geo/assets/{asset.id}"}
