from __future__ import annotations

import datetime
import uuid
from typing import Optional

from pydantic import BaseModel

from app.models.enums import CalendarEventType


class CalendarEventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_type: CalendarEventType
    event_date: datetime.date
    event_time: Optional[datetime.time] = None
    task_id: Optional[uuid.UUID] = None


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[CalendarEventType] = None
    event_date: Optional[datetime.date] = None
    event_time: Optional[datetime.time] = None


class CalendarEventOut(BaseModel):
    id: uuid.UUID
    startup_id: uuid.UUID
    title: str
    description: Optional[str] = None
    event_type: CalendarEventType
    event_date: datetime.date
    event_time: Optional[datetime.time] = None
    task_id: Optional[uuid.UUID] = None
    created_by_user: Optional[uuid.UUID] = None
    created_by_agent: Optional[uuid.UUID] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
