import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Table, Text
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


# --- Growth Grid ---------------------------------------------------------
# Moments are need states read as category entry points, not audiences.
# See frameworks/growth-grid.md.


class Moment(str, enum.Enum):
    REPLENISH = "replenish"
    PLAN = "plan"
    DISCOVER = "discover"
    MANAGE = "manage"
    CELEBRATE = "celebrate"
    CARE = "care"


class IntentDomain(str, enum.Enum):
    FUNC = "FUNC"
    EMOT = "EMOT"
    SOCL = "SOCL"
    CTXT = "CTXT"
    COGN = "COGN"
    AGNT = "AGNT"


class Grid(Base):
    __tablename__ = "grids"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(255))
    market: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    moment_settings: Mapped[list["MomentSetting"]] = relationship(
        back_populates="grid", cascade="all, delete-orphan"
    )
    intent_scores: Mapped[list["IntentScore"]] = relationship(
        back_populates="grid", cascade="all, delete-orphan", order_by="IntentScore.taxonomy_id"
    )
    angles: Mapped[list["Angle"]] = relationship(
        back_populates="grid", cascade="all, delete-orphan", order_by="Angle.id"
    )


class MomentSetting(Base):
    """Per-grid delegation prior for a Moment (hypothesis, editable)."""

    __tablename__ = "moment_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    grid_id: Mapped[int] = mapped_column(ForeignKey("grids.id", ondelete="CASCADE"))
    moment: Mapped[Moment] = mapped_column(Enum(Moment))
    delegation_prior: Mapped[float] = mapped_column(Float)

    grid: Mapped["Grid"] = relationship(back_populates="moment_settings")


class IntentScore(Base):
    """One scored intent from the 47-intent taxonomy (or a CUSTOM- flex)."""

    __tablename__ = "intent_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    grid_id: Mapped[int] = mapped_column(ForeignKey("grids.id", ondelete="CASCADE"))
    taxonomy_id: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(255))
    domain: Mapped[IntentDomain] = mapped_column(Enum(IntentDomain))
    # None = cross-state modulator (most AGNT intents)
    moment: Mapped[Moment | None] = mapped_column(Enum(Moment), default=None)
    importance: Mapped[int] = mapped_column(Integer)
    delivery: Mapped[int] = mapped_column(Integer)

    grid: Mapped["Grid"] = relationship(back_populates="intent_scores")

    @property
    def gap(self) -> int:
        return self.importance - self.delivery

    @property
    def is_modulator(self) -> bool:
        return self.moment is None


class Angle(Base):
    """A creative-signal Angle. Moments reach the market through creative, never audience."""

    __tablename__ = "angles"

    id: Mapped[int] = mapped_column(primary_key=True)
    grid_id: Mapped[int] = mapped_column(ForeignKey("grids.id", ondelete="CASCADE"))
    moment: Mapped[Moment | None] = mapped_column(Enum(Moment), default=None)  # None = CROSS
    name: Mapped[str] = mapped_column(String(255))
    mindset: Mapped[str] = mapped_column(String(100))
    messaging: Mapped[str] = mapped_column(String(100))
    proof: Mapped[str | None] = mapped_column(String(100), default=None)
    context: Mapped[str | None] = mapped_column(String(100), default=None)

    grid: Mapped["Grid"] = relationship(back_populates="angles")
