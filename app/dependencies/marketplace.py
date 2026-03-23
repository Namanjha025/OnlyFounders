from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.marketplace_profile import MarketplaceProfile
from app.models.user import User


async def get_my_marketplace_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MarketplaceProfile:
    result = await db.execute(
        select(MarketplaceProfile)
        .where(MarketplaceProfile.user_id == current_user.id)
        .options(
            selectinload(MarketplaceProfile.professional_data),
            selectinload(MarketplaceProfile.advisor_data),
            selectinload(MarketplaceProfile.founder_data),
            selectinload(MarketplaceProfile.documents),
            selectinload(MarketplaceProfile.user),
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marketplace profile not found",
        )
    return profile


async def get_marketplace_profile_or_404(
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> MarketplaceProfile:
    result = await db.execute(
        select(MarketplaceProfile)
        .where(MarketplaceProfile.id == profile_id)
        .options(
            selectinload(MarketplaceProfile.professional_data),
            selectinload(MarketplaceProfile.advisor_data),
            selectinload(MarketplaceProfile.founder_data),
            selectinload(MarketplaceProfile.documents),
            selectinload(MarketplaceProfile.user),
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marketplace profile not found",
        )
    return profile
