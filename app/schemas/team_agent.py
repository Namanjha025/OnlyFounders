from __future__ import annotations

import datetime
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TeamAgentCreate(BaseModel):
    agent_id: uuid.UUID
    role: Optional[str] = None
    job_description: Optional[str] = None


class TeamAgentUpdate(BaseModel):
    role: Optional[str] = None
    job_description: Optional[str] = None


class TeamAgentOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    agent_id: uuid.UUID
    role: Optional[str] = None
    job_description: Optional[str] = None
    agent_name: Optional[str] = None
    agent_slug: Optional[str] = None
    agent_description: Optional[str] = None
    agent_category: Optional[str] = None
    agent_icon: Optional[str] = None
    agent_color: Optional[str] = None
    agent_capabilities: Optional[Any] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
