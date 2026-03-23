from __future__ import annotations

import datetime
import uuid
from typing import List, Optional

from pydantic import BaseModel

from app.models.enums import CaseStatus, WorkspaceMessageRole, WorkspaceType


class WorkspaceCreate(BaseModel):
    name: str
    workspace_type: WorkspaceType = WorkspaceType.ONGOING
    case_status: CaseStatus = CaseStatus.OPEN
    goal: Optional[str] = None
    icon: Optional[str] = None


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    brief: Optional[str] = None
    status_text: Optional[str] = None
    progress: Optional[int] = None
    icon: Optional[str] = None
    case_status: Optional[CaseStatus] = None


class WorkspaceAgentOut(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    agent_name: Optional[str] = None
    agent_slug: Optional[str] = None
    agent_description: Optional[str] = None
    agent_category: Optional[str] = None
    agent_icon: Optional[str] = None
    agent_color: Optional[str] = None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class WorkspaceTaskOut(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    assignee_name: Optional[str] = None
    is_done: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class WorkspaceTaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_name: Optional[str] = None
    agent_id: Optional[uuid.UUID] = None


class WorkspaceTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_name: Optional[str] = None
    is_done: Optional[bool] = None


class WorkspaceMessageOut(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None
    role: WorkspaceMessageRole
    content: str
    action_buttons: Optional[dict] = None
    agent_name: Optional[str] = None
    agent_icon: Optional[str] = None
    agent_color: Optional[str] = None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class WorkspaceMessageCreate(BaseModel):
    content: str
    agent_id: Optional[uuid.UUID] = None
    role: Optional[str] = None


class WorkspaceOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    workspace_type: WorkspaceType
    case_status: CaseStatus = CaseStatus.OPEN
    goal: Optional[str] = None
    brief: Optional[str] = None
    status_text: Optional[str] = None
    progress: Optional[int] = None
    icon: Optional[str] = None
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    agents: List[WorkspaceAgentOut] = []
    tasks: List[WorkspaceTaskOut] = []
    notification_count: int = 0

    model_config = {"from_attributes": True}


class WorkspaceSummary(BaseModel):
    id: uuid.UUID
    name: str
    workspace_type: WorkspaceType
    case_status: CaseStatus = CaseStatus.OPEN
    icon: Optional[str] = None
    status_text: Optional[str] = None
    progress: Optional[int] = None
    agent_count: int = 0
    task_done_count: int = 0
    task_total_count: int = 0
    notification_count: int = 0
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
