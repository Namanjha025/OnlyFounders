from __future__ import annotations

import datetime
import uuid
from typing import Any, Optional

from pydantic import BaseModel

from app.models.enums import NotificationPriority, NotificationType


class NotificationOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    workspace_id: Optional[uuid.UUID] = None
    agent_id: Optional[uuid.UUID] = None
    notification_type: NotificationType
    priority: NotificationPriority
    title: str
    description: Optional[str] = None
    detail: Optional[str] = None
    is_read: bool
    action_buttons: Optional[Any] = None
    agent_name: Optional[str] = None
    agent_icon: Optional[str] = None
    agent_color: Optional[str] = None
    workspace_name: Optional[str] = None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class NotificationCreate(BaseModel):
    workspace_id: Optional[uuid.UUID] = None
    agent_id: Optional[uuid.UUID] = None
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.LOW
    title: str
    description: Optional[str] = None
    detail: Optional[str] = None
    action_buttons: Optional[Any] = None
