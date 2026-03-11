from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.enums import MemberDocCategory


class MemberDocUploadURLRequest(BaseModel):
    file_name: str
    category: MemberDocCategory
    mime_type: str


class MemberDocUploadURLResponse(BaseModel):
    upload_url: str
    s3_key: str


class MemberDocConfirmRequest(BaseModel):
    s3_key: str
    name: str
    category: MemberDocCategory
    file_name: str
    file_size: int
    mime_type: str


class MemberDocOut(BaseModel):
    id: uuid.UUID
    startup_id: uuid.UUID
    member_id: uuid.UUID
    name: str
    category: MemberDocCategory
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    s3_key: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
