from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel

from app.models.enums import MessageRole


class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: uuid.UUID
    startup_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    role: MessageRole
    content: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}
