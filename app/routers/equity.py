from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.startup import require_startup_owner
from app.models.equity import EquityShareholder
from app.models.startup import Startup
from app.schemas.equity import EquityShareholderCreate, EquityShareholderOut, EquityShareholderUpdate

router = APIRouter(prefix="/api/v1/startups/{startup_id}/equity", tags=["equity"])


@router.get("/", response_model=List[EquityShareholderOut])
async def list_shareholders(
    startup: Startup = Depends(require_startup_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EquityShareholder).where(EquityShareholder.startup_id == startup.id)
    )
    return [EquityShareholderOut.model_validate(e) for e in result.scalars().all()]


@router.post("/", response_model=EquityShareholderOut, status_code=status.HTTP_201_CREATED)
async def add_shareholder(
    data: EquityShareholderCreate,
    startup: Startup = Depends(require_startup_owner),
    db: AsyncSession = Depends(get_db),
):
    entry = EquityShareholder(startup_id=startup.id, **data.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return EquityShareholderOut.model_validate(entry)


@router.put("/{entry_id}", response_model=EquityShareholderOut)
async def update_shareholder(
    entry_id: uuid.UUID,
    data: EquityShareholderUpdate,
    startup: Startup = Depends(require_startup_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EquityShareholder).where(
            EquityShareholder.id == entry_id, EquityShareholder.startup_id == startup.id
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shareholder not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)

    await db.commit()
    await db.refresh(entry)
    return EquityShareholderOut.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shareholder(
    entry_id: uuid.UUID,
    startup: Startup = Depends(require_startup_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EquityShareholder).where(
            EquityShareholder.id == entry_id, EquityShareholder.startup_id == startup.id
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shareholder not found")
    await db.delete(entry)
    await db.commit()
