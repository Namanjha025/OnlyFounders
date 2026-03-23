from __future__ import annotations

import datetime
import uuid
from typing import Optional

from pydantic import BaseModel

from app.models.enums import FeedEventType


class FeedEventOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    workspace_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    event_type: FeedEventType
    title: str
    description: Optional[str] = None
    agent_name: Optional[str] = None
    agent_icon: Optional[str] = None
    agent_color: Optional[str] = None
    workspace_name: Optional[str] = None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class FeedEventCreate(BaseModel):
    workspace_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    event_type: FeedEventType
    title: str
    description: Optional[str] = None
