from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.enums import MemberRole


class StartupMemberCreate(BaseModel):
    user_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    email: Optional[str] = None
    role: MemberRole
    title: Optional[str] = None
    equity_percentage: Optional[float] = None
    is_full_time: Optional[bool] = None
    linkedin_url: Optional[str] = None
    bio: Optional[str] = None


class StartupMemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[MemberRole] = None
    title: Optional[str] = None
    equity_percentage: Optional[float] = None
    is_full_time: Optional[bool] = None
    linkedin_url: Optional[str] = None
    bio: Optional[str] = None


class StartupMemberOut(BaseModel):
    id: uuid.UUID
    startup_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    email: Optional[str] = None
    role: MemberRole
    title: Optional[str] = None
    equity_percentage: Optional[float] = None
    is_full_time: Optional[bool] = None
    linkedin_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
