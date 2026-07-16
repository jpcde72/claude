import json

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GeoAudit
from app.services.geo.audit_service import ALL_SURFACES, audit_report, run_audit

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _audit_context(db: Session) -> dict:
    audits = db.query(GeoAudit).order_by(GeoAudit.created_at.desc()).all()
    return {"audits": audits, "all_surfaces": ALL_SURFACES}


@router.get("/geo", response_class=HTMLResponse)
def geo_dashboard(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request,
        "geo_index.html", {"request": request, **_audit_context(db)}
    )


@router.post("/geo/audits", response_class=HTMLResponse)
def create_audit(
    request: Request,
    brand: str = Form(...),
    brand_domain: str = Form(""),
    competitors: str = Form(""),
    terms: str = Form(...),
    surfaces: list[str] = Form(ALL_SURFACES),
    db: Session = Depends(get_db),
):
    try:
        run_audit(
            db,
            brand=brand,
            terms_raw=terms,
            surfaces=surfaces,
            brand_domain=brand_domain,
            competitors_raw=competitors,
        )
    except ValueError as exc:
        return HTMLResponse(f"<p class='error'>{exc}</p>", status_code=422)
    return templates.TemplateResponse(
        request,
        "partials/geo_audit_list.html", {"request": request, **_audit_context(db)}
    )


@router.get("/geo/audits/{audit_id}", response_class=HTMLResponse)
def audit_detail(request: Request, audit_id: int, db: Session = Depends(get_db)):
    audit = db.query(GeoAudit).get(audit_id)
    if not audit:
        return HTMLResponse("<p>Audit not found</p>", status_code=404)
    report = audit_report(audit)
    return templates.TemplateResponse(
        request,
        "geo_audit_detail.html",
        {"request": request, "audit": audit, "report": report},
    )


@router.delete("/geo/audits/{audit_id}", response_class=HTMLResponse)
def delete_audit(audit_id: int, db: Session = Depends(get_db)):
    audit = db.query(GeoAudit).get(audit_id)
    if audit:
        db.delete(audit)
        db.commit()
    return HTMLResponse("")


# --- JSON API (used by the /geo-audit skill and integrations) ---


class AuditRequest(BaseModel):
    brand: str
    brand_domain: str = ""
    competitors: list[str] = Field(default_factory=list)
    terms: list[str]
    surfaces: list[str] = Field(default_factory=lambda: list(ALL_SURFACES))


@router.post("/api/geo/audits")
def api_create_audit(payload: AuditRequest, db: Session = Depends(get_db)):
    try:
        audit = run_audit(
            db,
            brand=payload.brand,
            terms_raw="\n".join(payload.terms),
            surfaces=payload.surfaces,
            brand_domain=payload.brand_domain,
            competitors_raw=", ".join(payload.competitors),
        )
    except ValueError as exc:
        return JSONResponse({"detail": str(exc)}, status_code=422)
    return audit_report(audit)


@router.get("/api/geo/audits/{audit_id}")
def api_audit_detail(audit_id: int, db: Session = Depends(get_db)):
    audit = db.query(GeoAudit).get(audit_id)
    if not audit:
        return JSONResponse({"detail": "Audit not found"}, status_code=404)
    return audit_report(audit)


@router.get("/api/geo/audits")
def api_audit_list(db: Session = Depends(get_db)):
    audits = db.query(GeoAudit).order_by(GeoAudit.created_at.desc()).all()
    return [
        {
            "id": a.id,
            "brand": a.brand,
            "status": a.status.value,
            "data_mode": a.data_mode,
            "surfaces": a.surfaces.split(","),
            "term_count": len(a.terms.splitlines()),
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "scorecard": json.loads(a.scorecard_json) if a.scorecard_json else None,
        }
        for a in audits
    ]
