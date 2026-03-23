from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ENUM, JSONB, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import (
    AvailabilityStatus,
    CommitmentLevel,
    FeeStructure,
    Industry,
    MarketplaceDocumentType,
    ProfileType,
    StartupStage,
)


class MarketplaceProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "marketplace_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, nullable=False,
    )
    profile_type: Mapped[str] = mapped_column(String(20), nullable=False)
    headline: Mapped[Optional[str]] = mapped_column(String(500))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    skills: Mapped[Optional[dict]] = mapped_column(JSONB, server_default="[]")
    skills_text: Mapped[Optional[str]] = mapped_column(Text)
    linkedin_url: Mapped[Optional[str]] = mapped_column(Text)
    website_url: Mapped[Optional[str]] = mapped_column(Text)
    profile_score: Mapped[int] = mapped_column(Integer, server_default="0")
    is_public: Mapped[bool] = mapped_column(Boolean, server_default="false")
    visibility_settings: Mapped[Optional[dict]] = mapped_column(JSONB, server_default="{}")
    extra_data: Mapped[Optional[dict]] = mapped_column(JSONB, server_default="{}")
    twin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True,  # FK to twins deferred until twins table exists
    )
    profile_views: Mapped[int] = mapped_column(Integer, server_default="0")
    search_vector = mapped_column(TSVECTOR, nullable=True)

    # Relationships
    user = relationship("User", back_populates="marketplace_profile")
    professional_data = relationship(
        "ProfessionalProfile", back_populates="profile",
        uselist=False, cascade="all, delete-orphan",
    )
    advisor_data = relationship(
        "AdvisorProfile", back_populates="profile",
        uselist=False, cascade="all, delete-orphan",
    )
    founder_data = relationship(
        "FounderMarketplaceProfile", back_populates="profile",
        uselist=False, cascade="all, delete-orphan",
    )
    documents = relationship(
        "ProfileDocument", back_populates="profile",
        cascade="all, delete-orphan",
    )

    @property
    def type_profile(self):
        if self.profile_type == ProfileType.PROFESSIONAL.value:
            return self.professional_data
        if self.profile_type == ProfileType.ADVISOR.value:
            return self.advisor_data
        if self.profile_type == ProfileType.FOUNDER.value:
            return self.founder_data
        return None

    __table_args__ = (
        CheckConstraint(
            "profile_type IN ('founder', 'professional', 'advisor')",
            name="ck_mp_profile_type",
        ),
        Index("ix_mp_search_vector", "search_vector", postgresql_using="gin"),
        Index("ix_mp_skills", "skills", postgresql_using="gin"),
        Index(
            "ix_mp_headline_trgm", "headline",
            postgresql_using="gin",
            postgresql_ops={"headline": "gin_trgm_ops"},
        ),
        Index("ix_mp_public_type", "is_public", "profile_type"),
    )


class ProfessionalProfile(Base, TimestampMixin):
    __tablename__ = "professional_profiles"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("marketplace_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    primary_role: Mapped[Optional[str]] = mapped_column(String(100))
    years_experience: Mapped[Optional[int]] = mapped_column(Integer)
    hourly_rate: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    availability_status: Mapped[Optional[AvailabilityStatus]] = mapped_column(
        ENUM(AvailabilityStatus, name="availabilitystatus", create_type=True,
             values_callable=lambda e: [x.value for x in e]),
    )
    employment_type_preference: Mapped[Optional[dict]] = mapped_column(JSONB, server_default="[]")
    portfolio_url: Mapped[Optional[str]] = mapped_column(Text)
    certifications: Mapped[Optional[dict]] = mapped_column(JSONB, server_default="[]")
    service_offerings: Mapped[Optional[dict]] = mapped_column(JSONB, server_default="[]")
    cal_booking_link: Mapped[Optional[str]] = mapped_column(Text)

    profile = relationship("MarketplaceProfile", back_populates="professional_data")


class AdvisorProfile(Base, TimestampMixin):
    __tablename__ = "advisor_profiles"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("marketplace_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    domain_expertise: Mapped[Optional[dict]] = mapped_column(JSONB, server_default="[]")
    investment_thesis: Mapped[Optional[str]] = mapped_column(Text)
    portfolio_companies: Mapped[Optional[dict]] = mapped_column(JSONB, server_default="[]")
    investment_stages: Mapped[Optional[dict]] = mapped_column(JSONB, server_default="[]")
    check_size_min: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    check_size_max: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    fee_structure: Mapped[Optional[FeeStructure]] = mapped_column(
        ENUM(FeeStructure, name="feestructure", create_type=True,
             values_callable=lambda e: [x.value for x in e]),
    )
    availability: Mapped[Optional[str]] = mapped_column(String(50))
    cal_booking_link: Mapped[Optional[str]] = mapped_column(Text)

    profile = relationship("MarketplaceProfile", back_populates="advisor_data")


class FounderMarketplaceProfile(Base, TimestampMixin):
    __tablename__ = "founder_marketplace_profiles"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("marketplace_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    startup_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="SET NULL"), nullable=True,
    )
    looking_for_roles: Mapped[Optional[dict]] = mapped_column(JSONB, server_default="[]")
    equity_offered: Mapped[Optional[str]] = mapped_column(String(50))
    startup_stage: Mapped[Optional[StartupStage]] = mapped_column(
        ENUM(StartupStage, name="startupstage", create_type=False,
             values_callable=lambda e: [x.value for x in e]),
    )
    industry: Mapped[Optional[Industry]] = mapped_column(
        ENUM(Industry, name="industry", create_type=False,
             values_callable=lambda e: [x.value for x in e]),
    )
    cofounder_brief: Mapped[Optional[str]] = mapped_column(Text)
    commitment_level: Mapped[Optional[CommitmentLevel]] = mapped_column(
        ENUM(CommitmentLevel, name="commitmentlevel", create_type=True,
             values_callable=lambda e: [x.value for x in e]),
    )
    remote_ok: Mapped[Optional[bool]] = mapped_column(Boolean, server_default="true")
    funding_stage: Mapped[Optional[str]] = mapped_column(String(50))

    profile = relationship("MarketplaceProfile", back_populates="founder_data")


class ProfileDocument(Base, UUIDMixin):
    __tablename__ = "profile_documents"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("marketplace_profiles.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    document_type: Mapped[Optional[MarketplaceDocumentType]] = mapped_column(
        ENUM(MarketplaceDocumentType, name="marketplacedocumenttype", create_type=True,
             values_callable=lambda e: [x.value for x in e]),
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    s3_key: Mapped[str] = mapped_column(Text, nullable=False)
    s3_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))
    is_public: Mapped[bool] = mapped_column(Boolean, server_default="true")
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )

    profile = relationship("MarketplaceProfile", back_populates="documents")
