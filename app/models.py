import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IntentStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class GeoSurface(str, enum.Enum):
    GEMINI = "gemini"
    AI_MODE = "ai_mode"
    AI_OVERVIEW = "ai_overview"


class GeoAuditStatus(str, enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


task_dependencies = Table(
    "task_dependencies",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("depends_on_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
)


class Intent(Base):
    __tablename__ = "intents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, default=None)
    status: Mapped[IntentStatus] = mapped_column(
        Enum(IntentStatus), default=IntentStatus.DRAFT
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    plans: Mapped[list["Plan"]] = relationship(
        back_populates="intent", cascade="all, delete-orphan", order_by="Plan.order"
    )


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    intent_id: Mapped[int] = mapped_column(ForeignKey("intents.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, default=None)
    order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    intent: Mapped["Intent"] = relationship(back_populates="plans")
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan", order_by="Task.order"
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, default=None)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.PENDING
    )
    order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)

    plan: Mapped["Plan"] = relationship(back_populates="tasks")

    dependencies: Mapped[list["Task"]] = relationship(
        secondary=task_dependencies,
        primaryjoin=id == task_dependencies.c.task_id,
        secondaryjoin=id == task_dependencies.c.depends_on_id,
        backref="dependents",
    )


class GeoAudit(Base):
    __tablename__ = "geo_audits"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(255))
    brand_domain: Mapped[str | None] = mapped_column(String(255), default=None)
    competitors: Mapped[str | None] = mapped_column(Text, default=None)  # comma-separated
    terms: Mapped[str] = mapped_column(Text)  # newline-separated
    surfaces: Mapped[str] = mapped_column(String(255))  # comma-separated GeoSurface values
    status: Mapped[GeoAuditStatus] = mapped_column(
        Enum(GeoAuditStatus), default=GeoAuditStatus.RUNNING
    )
    data_mode: Mapped[str] = mapped_column(String(20), default="mock")  # live | mock | mixed
    scorecard_json: Mapped[str | None] = mapped_column(Text, default=None)
    insights_json: Mapped[str | None] = mapped_column(Text, default=None)
    error: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)

    results: Mapped[list["GeoQueryResult"]] = relationship(
        back_populates="audit", cascade="all, delete-orphan", order_by="GeoQueryResult.id"
    )


class GeoQueryResult(Base):
    __tablename__ = "geo_query_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    audit_id: Mapped[int] = mapped_column(
        ForeignKey("geo_audits.id", ondelete="CASCADE")
    )
    term: Mapped[str] = mapped_column(String(500))
    surface: Mapped[GeoSurface] = mapped_column(Enum(GeoSurface))
    provider_mode: Mapped[str] = mapped_column(String(20), default="mock")  # live | mock
    response_text: Mapped[str | None] = mapped_column(Text, default=None)
    mentioned: Mapped[bool] = mapped_column(default=False)
    mention_count: Mapped[int] = mapped_column(Integer, default=0)
    prominence: Mapped[float] = mapped_column(default=0.0)
    cited: Mapped[bool] = mapped_column(default=False)
    citations_json: Mapped[str | None] = mapped_column(Text, default=None)
    competitor_mentions_json: Mapped[str | None] = mapped_column(Text, default=None)
    sentiment_score: Mapped[float] = mapped_column(default=0.0)
    sentiment_label: Mapped[str] = mapped_column(String(20), default="not_mentioned")
    error: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    audit: Mapped["GeoAudit"] = relationship(back_populates="results")
