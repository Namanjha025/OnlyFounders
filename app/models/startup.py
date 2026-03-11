from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import Industry, StartupStage


class Startup(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "startups"

    created_by: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    tagline: Mapped[Optional[str]] = mapped_column(String(80))
    short_description: Mapped[Optional[str]] = mapped_column(String(500))
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    website_url: Mapped[Optional[str]] = mapped_column(String(500))
    stage: Mapped[Optional[StartupStage]] = mapped_column(
        ENUM(StartupStage, name="startupstage", create_type=True, values_callable=lambda e: [x.value for x in e])
    )
    industry: Mapped[Optional[Industry]] = mapped_column(
        ENUM(Industry, name="industry", create_type=True, values_callable=lambda e: [x.value for x in e])
    )
    founded_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    hq_city: Mapped[Optional[str]] = mapped_column(String(100))
    hq_country: Mapped[Optional[str]] = mapped_column(String(100))
    is_remote: Mapped[Optional[bool]] = mapped_column(Boolean)
    team_size: Mapped[Optional[int]] = mapped_column(Integer)

    creator = relationship("User", back_populates="startups")
    members = relationship("StartupMember", back_populates="startup", cascade="all, delete-orphan")
    product_detail = relationship("ProductDetail", back_populates="startup", uselist=False, cascade="all, delete-orphan")
    traction_metric = relationship("TractionMetric", back_populates="startup", uselist=False, cascade="all, delete-orphan")
    financial_detail = relationship("FinancialDetail", back_populates="startup", uselist=False, cascade="all, delete-orphan")
    funding_rounds = relationship("FundingRound", back_populates="startup", cascade="all, delete-orphan")
    equity_shareholders = relationship("EquityShareholder", back_populates="startup", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="startup", cascade="all, delete-orphan")
