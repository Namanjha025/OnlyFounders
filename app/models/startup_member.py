from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, Date, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import AccessLevel, EmploymentType, MemberRole


class StartupMember(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "startup_members"
    __table_args__ = (
        UniqueConstraint("startup_id", "user_id", name="uq_startup_member_user"),
        UniqueConstraint("startup_id", "agent_id", name="uq_startup_member_agent"),
    )

    startup_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    # Human member (platform user)
    user_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    # Agent member
    agent_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL")
    )
    name: Mapped[Optional[str]] = mapped_column(String(200))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[MemberRole] = mapped_column(
        ENUM(MemberRole, name="memberrole", create_type=True), nullable=False
    )
    title: Mapped[Optional[str]] = mapped_column(String(100))
    department: Mapped[Optional[str]] = mapped_column(String(100))
    responsibilities: Mapped[Optional[str]] = mapped_column(Text)
    access_level: Mapped[Optional[AccessLevel]] = mapped_column(
        ENUM(AccessLevel, name="accesslevel", create_type=True)
    )
    employment_type: Mapped[Optional[EmploymentType]] = mapped_column(
        ENUM(EmploymentType, name="employmenttype", create_type=True)
    )
    start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    salary: Mapped[Optional[int]] = mapped_column(BigInteger)
    equity_percentage: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    is_full_time: Mapped[Optional[bool]] = mapped_column(Boolean)
    reporting_to: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startup_members.id", ondelete="SET NULL")
    )
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    bio: Mapped[Optional[str]] = mapped_column(Text)

    startup = relationship("Startup", back_populates="members")
    agent = relationship("Agent")
    documents = relationship("MemberDocument", back_populates="member", cascade="all, delete-orphan")
    manager = relationship("StartupMember", remote_side="StartupMember.id")
