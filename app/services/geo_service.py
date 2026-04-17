from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import GeoRegion, RegionType
from app.schemas import GeoRegionCreate, GeoRegionUpdate


def create_region(db: Session, data: GeoRegionCreate) -> GeoRegion:
    if data.parent_id is not None:
        parent = db.query(GeoRegion).get(data.parent_id)
        if not parent:
            raise ValueError(f"Parent region {data.parent_id} not found")

    region = GeoRegion(**data.model_dump())
    db.add(region)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(f"Region with code '{data.code}' already exists")
    db.refresh(region)
    return region


def get_region(db: Session, region_id: int) -> GeoRegion:
    region = db.query(GeoRegion).get(region_id)
    if not region:
        raise ValueError(f"Region {region_id} not found")
    return region


def list_regions(
    db: Session,
    region_type: RegionType | None = None,
    parent_id: int | None = None,
) -> list[GeoRegion]:
    query = db.query(GeoRegion)
    if region_type is not None:
        query = query.filter(GeoRegion.region_type == region_type)
    if parent_id is not None:
        query = query.filter(GeoRegion.parent_id == parent_id)
    return query.order_by(GeoRegion.name).all()


def update_region(db: Session, region_id: int, data: GeoRegionUpdate) -> GeoRegion:
    region = db.query(GeoRegion).get(region_id)
    if not region:
        raise ValueError(f"Region {region_id} not found")

    update_data = data.model_dump(exclude_unset=True)

    if "parent_id" in update_data and update_data["parent_id"] is not None:
        if update_data["parent_id"] == region_id:
            raise ValueError("A region cannot be its own parent")
        parent = db.query(GeoRegion).get(update_data["parent_id"])
        if not parent:
            raise ValueError(f"Parent region {update_data['parent_id']} not found")
        if _is_descendant(db, update_data["parent_id"], region_id):
            raise ValueError("Cannot set parent: would create circular hierarchy")

    for field, value in update_data.items():
        setattr(region, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(f"Region with code '{data.code}' already exists")
    db.refresh(region)
    return region


def delete_region(db: Session, region_id: int) -> None:
    region = db.query(GeoRegion).get(region_id)
    if not region:
        raise ValueError(f"Region {region_id} not found")
    db.delete(region)
    db.commit()


def get_children(db: Session, region_id: int) -> list[GeoRegion]:
    region = db.query(GeoRegion).get(region_id)
    if not region:
        raise ValueError(f"Region {region_id} not found")
    return (
        db.query(GeoRegion)
        .filter(GeoRegion.parent_id == region_id)
        .order_by(GeoRegion.name)
        .all()
    )


def _is_descendant(db: Session, candidate_id: int, of_id: int) -> bool:
    current_id = candidate_id
    visited: set[int] = set()
    while current_id is not None:
        if current_id == of_id:
            return True
        if current_id in visited:
            break
        visited.add(current_id)
        parent = db.query(GeoRegion).get(current_id)
        if parent is None:
            break
        current_id = parent.parent_id
    return False
