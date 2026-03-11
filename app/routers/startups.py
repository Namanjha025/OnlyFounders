from __future__ import annotations

import re
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.startup import require_startup_access
from app.models.startup import Startup
from app.models.user import User
from app.schemas.startup import StartupCreate, StartupOut, StartupUpdate

router = APIRouter(prefix="/api/v1/startups", tags=["startups"])


def _slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


async def _unique_slug(db: AsyncSession, base_slug: str) -> str:
    slug = base_slug
    counter = 1
    while True:
        result = await db.execute(select(Startup).where(Startup.slug == slug))
        if result.scalar_one_or_none() is None:
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


@router.post("/", response_model=StartupOut, status_code=status.HTTP_201_CREATED)
async def create_startup(
    data: StartupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    slug = await _unique_slug(db, _slugify(data.name))
    startup = Startup(
        created_by=current_user.id,
        slug=slug,
        **data.model_dump(),
    )
    db.add(startup)
    await db.commit()
    await db.refresh(startup)
    return StartupOut.model_validate(startup)


@router.get("/mine", response_model=List[StartupOut])
async def list_my_startups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Startup).where(Startup.created_by == current_user.id).order_by(Startup.created_at.desc())
    )
    return [StartupOut.model_validate(s) for s in result.scalars().all()]


@router.get("/{startup_id}", response_model=StartupOut)
async def get_startup(
    startup_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Startup).where(Startup.id == startup_id))
    startup = result.scalar_one_or_none()
    if not startup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")
    return StartupOut.model_validate(startup)


@router.put("/{startup_id}", response_model=StartupOut)
async def update_startup(
    data: StartupUpdate,
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] != startup.name:
        startup.slug = await _unique_slug(db, _slugify(update_data["name"]))

    for key, value in update_data.items():
        setattr(startup, key, value)

    await db.commit()
    await db.refresh(startup)
    return StartupOut.model_validate(startup)
