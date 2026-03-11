from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import Date, ForeignKey, String, Text, Time
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import CalendarEventType


class CalendarEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "calendar_events"

    startup_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    event_type: Mapped[CalendarEventType] = mapped_column(
        ENUM(CalendarEventType, name="calendareventtype", create_type=True), nullable=False
    )
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    event_time: Mapped[Optional[datetime.time]] = mapped_column(Time)
    task_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE")
    )
    created_by_user: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    created_by_agent: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True)
    )

    startup = relationship("Startup", backref="calendar_events")
    task = relationship("Task", backref="calendar_events")
