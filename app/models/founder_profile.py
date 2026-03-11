from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class FounderProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "founder_profiles"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    twitter_url: Mapped[Optional[str]] = mapped_column(String(500))
    github_url: Mapped[Optional[str]] = mapped_column(String(500))
    website_url: Mapped[Optional[str]] = mapped_column(String(500))
    profile_photo_url: Mapped[Optional[str]] = mapped_column(String(500))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    country: Mapped[Optional[str]] = mapped_column(String(100))
    is_technical: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_full_time: Mapped[Optional[bool]] = mapped_column(Boolean)
    education: Mapped[Optional[str]] = mapped_column(String(255))
    degree_field: Mapped[Optional[str]] = mapped_column(String(255))
    years_of_experience: Mapped[Optional[int]] = mapped_column(Integer)
    previous_startups: Mapped[Optional[str]] = mapped_column(Text)
    notable_achievement: Mapped[Optional[str]] = mapped_column(Text)
    skills: Mapped[Optional[dict]] = mapped_column(JSONB)
    domain_expertise: Mapped[Optional[dict]] = mapped_column(JSONB)

    user = relationship("User", back_populates="founder_profile")
