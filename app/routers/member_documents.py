from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.startup import require_startup_access
from app.models.member_document import MemberDocument
from app.models.startup import Startup
from app.models.startup_member import StartupMember
from app.schemas.member_document import (
    MemberDocConfirmRequest,
    MemberDocOut,
    MemberDocUploadURLRequest,
    MemberDocUploadURLResponse,
)
from app.services.s3 import delete_s3_object, generate_download_presigned_url, generate_upload_presigned_url

router = APIRouter(
    prefix="/api/v1/startups/{startup_id}/members/{member_id}/documents",
    tags=["member-documents"],
)


async def _get_member_or_404(
    member_id: uuid.UUID, startup: Startup, db: AsyncSession
) -> StartupMember:
    result = await db.execute(
        select(StartupMember).where(
            StartupMember.id == member_id, StartupMember.startup_id == startup.id
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return member


@router.get("/", response_model=List[MemberDocOut])
async def list_member_documents(
    member_id: uuid.UUID,
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    await _get_member_or_404(member_id, startup, db)
    result = await db.execute(
        select(MemberDocument)
        .where(MemberDocument.member_id == member_id, MemberDocument.startup_id == startup.id)
        .order_by(MemberDocument.created_at.desc())
    )
    return [MemberDocOut.model_validate(d) for d in result.scalars().all()]


@router.post("/upload-url", response_model=MemberDocUploadURLResponse)
async def get_member_doc_upload_url(
    member_id: uuid.UUID,
    data: MemberDocUploadURLRequest,
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    await _get_member_or_404(member_id, startup, db)
    result = generate_upload_presigned_url(data.file_name, data.mime_type, str(startup.id))
    return MemberDocUploadURLResponse(**result)


@router.post("/confirm-upload", response_model=MemberDocOut, status_code=status.HTTP_201_CREATED)
async def confirm_member_doc_upload(
    member_id: uuid.UUID,
    data: MemberDocConfirmRequest,
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    await _get_member_or_404(member_id, startup, db)
    doc = MemberDocument(
        startup_id=startup.id,
        member_id=member_id,
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
    return MemberDocOut.model_validate(doc)


@router.get("/{doc_id}/download-url")
async def get_member_doc_download_url(
    member_id: uuid.UUID,
    doc_id: uuid.UUID,
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MemberDocument).where(
            MemberDocument.id == doc_id,
            MemberDocument.member_id == member_id,
            MemberDocument.startup_id == startup.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if not doc.s3_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file associated")
    url = generate_download_presigned_url(doc.s3_key)
    return {"download_url": url}


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member_document(
    member_id: uuid.UUID,
    doc_id: uuid.UUID,
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MemberDocument).where(
            MemberDocument.id == doc_id,
            MemberDocument.member_id == member_id,
            MemberDocument.startup_id == startup.id,
        )
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
