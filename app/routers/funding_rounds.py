from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.startup import require_startup_owner
from app.models.funding_round import FundingRound
from app.models.startup import Startup
from app.schemas.funding_round import FundingRoundCreate, FundingRoundOut, FundingRoundUpdate

router = APIRouter(prefix="/api/v1/startups/{startup_id}/funding-rounds", tags=["funding-rounds"])


@router.get("/", response_model=List[FundingRoundOut])
async def list_rounds(
    startup: Startup = Depends(require_startup_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FundingRound)
        .where(FundingRound.startup_id == startup.id)
        .order_by(FundingRound.round_date.desc().nulls_last())
    )
    return [FundingRoundOut.model_validate(r) for r in result.scalars().all()]


@router.post("/", response_model=FundingRoundOut, status_code=status.HTTP_201_CREATED)
async def add_round(
    data: FundingRoundCreate,
    startup: Startup = Depends(require_startup_owner),
    db: AsyncSession = Depends(get_db),
):
    funding_round = FundingRound(startup_id=startup.id, **data.model_dump())
    db.add(funding_round)
    await db.commit()
    await db.refresh(funding_round)
    return FundingRoundOut.model_validate(funding_round)


@router.put("/{round_id}", response_model=FundingRoundOut)
async def update_round(
    round_id: uuid.UUID,
    data: FundingRoundUpdate,
    startup: Startup = Depends(require_startup_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FundingRound).where(
            FundingRound.id == round_id, FundingRound.startup_id == startup.id
        )
    )
    funding_round = result.scalar_one_or_none()
    if not funding_round:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funding round not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(funding_round, key, value)

    await db.commit()
    await db.refresh(funding_round)
    return FundingRoundOut.model_validate(funding_round)


@router.delete("/{round_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_round(
    round_id: uuid.UUID,
    startup: Startup = Depends(require_startup_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FundingRound).where(
            FundingRound.id == round_id, FundingRound.startup_id == startup.id
        )
    )
    funding_round = result.scalar_one_or_none()
    if not funding_round:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funding round not found")
    await db.delete(funding_round)
    await db.commit()
