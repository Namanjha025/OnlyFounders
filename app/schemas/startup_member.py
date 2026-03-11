from __future__ import annotations

import datetime
import uuid
from typing import Optional

from pydantic import BaseModel

from app.models.enums import AccessLevel, EmploymentType, MemberRole


class StartupMemberCreate(BaseModel):
    user_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    email: Optional[str] = None
    role: MemberRole
    title: Optional[str] = None
    department: Optional[str] = None
    responsibilities: Optional[str] = None
    access_level: Optional[AccessLevel] = None
    employment_type: Optional[EmploymentType] = None
    start_date: Optional[datetime.date] = None
    salary: Optional[int] = None
    equity_percentage: Optional[float] = None
    is_full_time: Optional[bool] = None
    reporting_to: Optional[uuid.UUID] = None
    linkedin_url: Optional[str] = None
    bio: Optional[str] = None


class StartupMemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[MemberRole] = None
    title: Optional[str] = None
    department: Optional[str] = None
    responsibilities: Optional[str] = None
    access_level: Optional[AccessLevel] = None
    employment_type: Optional[EmploymentType] = None
    start_date: Optional[datetime.date] = None
    salary: Optional[int] = None
    equity_percentage: Optional[float] = None
    is_full_time: Optional[bool] = None
    reporting_to: Optional[uuid.UUID] = None
    linkedin_url: Optional[str] = None
    bio: Optional[str] = None


class StartupMemberOut(BaseModel):
    id: uuid.UUID
    startup_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    agent_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    email: Optional[str] = None
    role: MemberRole
    title: Optional[str] = None
    department: Optional[str] = None
    responsibilities: Optional[str] = None
    access_level: Optional[AccessLevel] = None
    employment_type: Optional[EmploymentType] = None
    start_date: Optional[datetime.date] = None
    salary: Optional[int] = None
    equity_percentage: Optional[float] = None
    is_full_time: Optional[bool] = None
    reporting_to: Optional[uuid.UUID] = None
    linkedin_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
