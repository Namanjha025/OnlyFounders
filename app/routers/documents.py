from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.startup import require_startup_access, require_startup_owner
from app.models.document import Document
from app.models.startup import Startup
from app.models.user import User
from app.schemas.document import (
    ConfirmUploadRequest,
    DocumentOut,
    DownloadURLResponse,
    UploadURLRequest,
    UploadURLResponse,
)
from app.services.s3 import delete_s3_object, generate_download_presigned_url, generate_upload_presigned_url

router = APIRouter(prefix="/api/v1/startups/{startup_id}/documents", tags=["documents"])


@router.get("/", response_model=List[DocumentOut])
async def list_documents(
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(Document.startup_id == startup.id).order_by(Document.created_at.desc())
    )
    return [DocumentOut.model_validate(d) for d in result.scalars().all()]


@router.post("/upload-url", response_model=UploadURLResponse)
async def get_upload_url(
    data: UploadURLRequest,
    startup: Startup = Depends(require_startup_access),
):
    result = generate_upload_presigned_url(data.file_name, data.mime_type, str(startup.id))
    return UploadURLResponse(**result)


@router.post("/confirm-upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def confirm_upload(
    data: ConfirmUploadRequest,
    startup: Startup = Depends(require_startup_access),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = Document(
        startup_id=startup.id,
        uploaded_by=current_user.id,
        name=data.name,
        category=data.category,
        file_name=data.file_name,
        file_size=data.file_size,
        mime_type=data.mime_type,
        s3_key=data.s3_key,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return DocumentOut.model_validate(doc)


@router.get("/{doc_id}/download-url", response_model=DownloadURLResponse)
async def get_download_url(
    doc_id: uuid.UUID,
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.startup_id == startup.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if not doc.s3_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file associated")

    url = generate_download_presigned_url(doc.s3_key)
    return DownloadURLResponse(download_url=url)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: uuid.UUID,
    startup: Startup = Depends(require_startup_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.startup_id == startup.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if doc.s3_key:
        try:
            delete_s3_object(doc.s3_key)
        except Exception:
            pass
    await db.delete(doc)
    await db.commit()
