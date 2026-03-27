from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.models.enums import AgentType


class AgentCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    agent_type: AgentType = AgentType.PLATFORM
    system_prompt: Optional[str] = None
    skills: Optional[Any] = None
    tools_config: Optional[Dict[str, Any]] = None
    endpoint_url: Optional[str] = None
    agent_card: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    capabilities: Optional[Any] = None
    instructions: Optional[Any] = None
    connections: Optional[Any] = None


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    skills: Optional[Any] = None
    tools_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    endpoint_url: Optional[str] = None
    agent_card: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    capabilities: Optional[Any] = None
    instructions: Optional[Any] = None
    connections: Optional[Any] = None


class AgentRegister(BaseModel):
    """Register an external agent by providing its A2A-compatible URL."""
    agent_url: str


class AgentOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None
    agent_type: AgentType
    system_prompt: Optional[str] = None
    skills: Optional[Any] = None
    tools_config: Optional[Dict[str, Any]] = None
    is_active: bool
    endpoint_url: Optional[str] = None
    agent_card: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    capabilities: Optional[Any] = None
    instructions: Optional[Any] = None
    connections: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
