from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RegionType
from app.schemas import GeoRegionCreate, GeoRegionResponse, GeoRegionUpdate
from app.services.geo_service import (
    create_region,
    delete_region,
    get_children,
    get_region,
    list_regions,
    update_region,
)

router = APIRouter(prefix="/api/geo", tags=["geo"])


@router.post("/regions", response_model=GeoRegionResponse, status_code=201)
def create_geo_region(
    data: GeoRegionCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_region(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/regions", response_model=list[GeoRegionResponse])
def list_geo_regions(
    region_type: RegionType | None = Query(None),
    parent_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    return list_regions(db, region_type=region_type, parent_id=parent_id)


@router.get("/regions/{region_id}", response_model=GeoRegionResponse)
def get_geo_region(
    region_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_region(db, region_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/regions/{region_id}", response_model=GeoRegionResponse)
def update_geo_region(
    region_id: int,
    data: GeoRegionUpdate,
    db: Session = Depends(get_db),
):
    try:
        return update_region(db, region_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/regions/{region_id}", status_code=204)
def delete_geo_region(
    region_id: int,
    db: Session = Depends(get_db),
):
    try:
        delete_region(db, region_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/regions/{region_id}/children", response_model=list[GeoRegionResponse]
)
def list_geo_region_children(
    region_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_children(db, region_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
