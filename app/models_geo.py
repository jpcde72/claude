"""GEO Studio persistence: brand projects, versioned assets and LLM exchanges."""

import json
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

ASSET_KINDS = {
    "strategy": "Strategy",
    "readiness_brief": "Readiness brief",
    "action_plan": "Action plan",
    "probe_set": "Probe set",
    "audit": "Audit",
    "surface_memo": "Surface memo",
    "research": "Research",
    "llm_answer": "Claude answer",
    "note": "Note",
}


class BrandProject(Base):
    __tablename__ = "geo_projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    sector: Mapped[str | None] = mapped_column(String(255), default=None)
    market: Mapped[str | None] = mapped_column(String(255), default=None)
    segment: Mapped[str] = mapped_column(String(32), default="consumer")
    website: Mapped[str | None] = mapped_column(String(512), default=None)
    competitors: Mapped[str | None] = mapped_column(Text, default=None)
    notes: Mapped[str | None] = mapped_column(Text, default=None)
    ari_json: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    assets: Mapped[list["Asset"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Asset.updated_at.desc()",
    )
    exchanges: Mapped[list["LLMExchange"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="LLMExchange.created_at.desc()",
    )

    @property
    def ari(self) -> dict[str, int]:
        return json.loads(self.ari_json) if self.ari_json else {}


class Asset(Base):
    __tablename__ = "geo_assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("geo_projects.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(32), default="note")
    title: Mapped[str] = mapped_column(String(255))
    tags: Mapped[str | None] = mapped_column(String(512), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    project: Mapped["BrandProject"] = relationship(back_populates="assets")
    versions: Mapped[list["AssetVersion"]] = relationship(
        back_populates="asset",
        cascade="all, delete-orphan",
        order_by="AssetVersion.version.desc()",
    )

    @property
    def current(self) -> "AssetVersion | None":
        return self.versions[0] if self.versions else None

    @property
    def kind_label(self) -> str:
        return ASSET_KINDS.get(self.kind, self.kind)


class AssetVersion(Base):
    __tablename__ = "geo_asset_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("geo_assets.id", ondelete="CASCADE"))
    version: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(32), default="manual")
    change_note: Mapped[str | None] = mapped_column(String(512), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    asset: Mapped["Asset"] = relationship(back_populates="versions")


class LLMExchange(Base):
    __tablename__ = "geo_exchanges"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("geo_projects.id", ondelete="CASCADE"), default=None
    )
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text, default="")
    model: Mapped[str | None] = mapped_column(String(64), default=None)
    web_search: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["BrandProject | None"] = relationship(back_populates="exchanges")
