import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.founder_profile import FounderProfile
from app.models.user import User
from app.schemas.founder_profile import FounderProfileOut, FounderProfileUpdate

router = APIRouter(prefix="/api/v1/profile", tags=["founder-profile"])


@router.get("/me", response_model=FounderProfileOut)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FounderProfile).where(FounderProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return FounderProfileOut.model_validate(profile)


@router.put("/me", response_model=FounderProfileOut)
async def update_my_profile(
    data: FounderProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FounderProfile).where(FounderProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    update_data = data.model_dump(exclude_unset=True)

    if profile is None:
        profile = FounderProfile(user_id=current_user.id, **update_data)
        db.add(profile)
    else:
        for key, value in update_data.items():
            setattr(profile, key, value)

    await db.commit()
    await db.refresh(profile)
    return FounderProfileOut.model_validate(profile)


@router.get("/{user_id}", response_model=FounderProfileOut)
async def get_profile(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FounderProfile).where(FounderProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return FounderProfileOut.model_validate(profile)
