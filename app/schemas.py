from pydantic import BaseModel

from app.models import IntentStatus, TaskStatus


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
