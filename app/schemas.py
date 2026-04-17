from datetime import datetime

from pydantic import BaseModel

from app.models import IntentStatus, RegionType, TaskStatus


class IntentCreate(BaseModel):
    title: str
    description: str | None = None


class IntentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: IntentStatus | None = None


class PlanCreate(BaseModel):
    title: str
    description: str | None = None


class PlanUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class TaskCreate(BaseModel):
    title: str
    description: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None


class GeoRegionCreate(BaseModel):
    name: str
    code: str | None = None
    region_type: RegionType = RegionType.OTHER
    parent_id: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    boundary_json: str | None = None
    description: str | None = None


class GeoRegionUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    region_type: RegionType | None = None
    parent_id: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    boundary_json: str | None = None
    description: str | None = None


class GeoRegionResponse(BaseModel):
    id: int
    name: str
    code: str | None
    region_type: RegionType
    parent_id: int | None
    latitude: float | None
    longitude: float | None
    boundary_json: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
