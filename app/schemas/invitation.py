from __future__ import annotations

import datetime
import uuid
from typing import Optional

from pydantic import BaseModel

from app.models.enums import InvitationStatus, MemberRole


class InvitationCreate(BaseModel):
    invited_user_id: uuid.UUID
    role: MemberRole
    title: Optional[str] = None
    responsibilities: Optional[str] = None
    message: Optional[str] = None
    expires_at: Optional[datetime.datetime] = None


class InvitationOut(BaseModel):
    id: uuid.UUID
    startup_id: uuid.UUID
    invited_by: uuid.UUID
    invited_user_id: uuid.UUID
    role: MemberRole
    title: Optional[str] = None
    responsibilities: Optional[str] = None
    message: Optional[str] = None
    status: InvitationStatus
    expires_at: Optional[datetime.datetime] = None
    responded_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
