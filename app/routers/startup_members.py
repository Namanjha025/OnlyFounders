from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.startup import require_startup_owner
from app.models.startup import Startup
from app.models.startup_member import StartupMember
from app.models.user import User
from app.schemas.startup_member import StartupMemberCreate, StartupMemberOut, StartupMemberUpdate

router = APIRouter(prefix="/api/v1/startups/{startup_id}/members", tags=["team-members"])


@router.get("/", response_model=List[StartupMemberOut])
async def list_members(
    startup_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StartupMember).where(StartupMember.startup_id == startup_id)
    )
    return [StartupMemberOut.model_validate(m) for m in result.scalars().all()]


@router.post("/", response_model=StartupMemberOut, status_code=status.HTTP_201_CREATED)
async def add_member(
    data: StartupMemberCreate,
    startup: Startup = Depends(require_startup_owner),
    db: AsyncSession = Depends(get_db),
):
    member = StartupMember(startup_id=startup.id, **data.model_dump())
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return StartupMemberOut.model_validate(member)


@router.put("/{member_id}", response_model=StartupMemberOut)
async def update_member(
    member_id: uuid.UUID,
    data: StartupMemberUpdate,
    startup: Startup = Depends(require_startup_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StartupMember).where(
            StartupMember.id == member_id, StartupMember.startup_id == startup.id
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(member, key, value)

    await db.commit()
    await db.refresh(member)
    return StartupMemberOut.model_validate(member)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_id: uuid.UUID,
    startup: Startup = Depends(require_startup_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StartupMember).where(
            StartupMember.id == member_id, StartupMember.startup_id == startup.id
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    await db.delete(member)
    await db.commit()
