from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import TaskPriority, TaskStatus


class Task(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tasks"

    startup_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        ENUM(TaskStatus, name="taskstatus", create_type=True),
        nullable=False,
        server_default=TaskStatus.PENDING.value,
    )
    priority: Mapped[Optional[TaskPriority]] = mapped_column(
        ENUM(TaskPriority, name="taskpriority", create_type=True)
    )
    assigned_to: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startup_members.id", ondelete="SET NULL"), index=True
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startup_members.id", ondelete="SET NULL")
    )
    due_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

    startup = relationship("Startup", backref="tasks")
    assignee = relationship("StartupMember", foreign_keys=[assigned_to])
    creator = relationship("StartupMember", foreign_keys=[created_by])
