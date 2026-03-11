from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import MemberRole


class StartupMember(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "startup_members"
    __table_args__ = (
        UniqueConstraint("startup_id", "user_id", name="uq_startup_member_user"),
    )

    startup_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    name: Mapped[Optional[str]] = mapped_column(String(200))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[MemberRole] = mapped_column(
        ENUM(MemberRole, name="memberrole", create_type=True), nullable=False
    )
    title: Mapped[Optional[str]] = mapped_column(String(100))
    equity_percentage: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    is_full_time: Mapped[Optional[bool]] = mapped_column(Boolean)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    bio: Mapped[Optional[str]] = mapped_column(Text)

    startup = relationship("Startup", back_populates="members")
