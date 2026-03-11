from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import BusinessModel, IncorporationType, Industry, StartupStage, TargetMarket


class Startup(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "startups"

    created_by: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    tagline: Mapped[Optional[str]] = mapped_column(String(80))
    short_description: Mapped[Optional[str]] = mapped_column(String(500))
    long_description: Mapped[Optional[str]] = mapped_column(Text)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    website_url: Mapped[Optional[str]] = mapped_column(String(500))
    demo_url: Mapped[Optional[str]] = mapped_column(String(500))
    stage: Mapped[Optional[StartupStage]] = mapped_column(
        ENUM(StartupStage, name="startupstage", create_type=True)
    )
    industry: Mapped[Optional[Industry]] = mapped_column(
        ENUM(Industry, name="industry", create_type=True)
    )
    industries: Mapped[Optional[dict]] = mapped_column(JSONB)
    business_model: Mapped[Optional[BusinessModel]] = mapped_column(
        ENUM(BusinessModel, name="businessmodel", create_type=True)
    )
    target_market: Mapped[Optional[TargetMarket]] = mapped_column(
        ENUM(TargetMarket, name="targetmarket", create_type=True)
    )
    founded_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    is_incorporated: Mapped[Optional[bool]] = mapped_column(Boolean)
    entity_type: Mapped[Optional[IncorporationType]] = mapped_column(
        ENUM(IncorporationType, name="incorporationtype", create_type=True)
    )
    incorporation_country: Mapped[Optional[str]] = mapped_column(String(100))
    incorporation_state: Mapped[Optional[str]] = mapped_column(String(100))
    legal_entity_name: Mapped[Optional[str]] = mapped_column(String(255))
    hq_city: Mapped[Optional[str]] = mapped_column(String(100))
    hq_country: Mapped[Optional[str]] = mapped_column(String(100))
    is_remote: Mapped[Optional[bool]] = mapped_column(Boolean)
    company_linkedin: Mapped[Optional[str]] = mapped_column(String(500))
    company_twitter: Mapped[Optional[str]] = mapped_column(String(500))
    team_size: Mapped[Optional[int]] = mapped_column(Integer)
    profile_completeness: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    creator = relationship("User", back_populates="startups")
    members = relationship("StartupMember", back_populates="startup", cascade="all, delete-orphan")
    product_detail = relationship("ProductDetail", back_populates="startup", uselist=False, cascade="all, delete-orphan")
    traction_metric = relationship("TractionMetric", back_populates="startup", uselist=False, cascade="all, delete-orphan")
    financial_detail = relationship("FinancialDetail", back_populates="startup", uselist=False, cascade="all, delete-orphan")
    funding_rounds = relationship("FundingRound", back_populates="startup", cascade="all, delete-orphan")
    equity_shareholders = relationship("EquityShareholder", back_populates="startup", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="startup", cascade="all, delete-orphan")
