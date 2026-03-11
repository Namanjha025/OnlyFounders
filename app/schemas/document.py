from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.enums import DocumentCategory


class UploadURLRequest(BaseModel):
    file_name: str
    category: DocumentCategory
    mime_type: str


class UploadURLResponse(BaseModel):
    upload_url: str
    s3_key: str


class ConfirmUploadRequest(BaseModel):
    s3_key: str
    name: str
    category: DocumentCategory
    file_name: str
    file_size: int
    mime_type: str


class DocumentOut(BaseModel):
    id: uuid.UUID
    startup_id: uuid.UUID
    uploaded_by: uuid.UUID
    name: str
    category: DocumentCategory
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    s3_key: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DownloadURLResponse(BaseModel):
    download_url: str
