import uuid

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.startup import Startup
from app.models.startup_member import StartupMember
from app.models.user import User


async def get_startup_or_404(
    startup_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Startup:
    result = await db.execute(select(Startup).where(Startup.id == startup_id))
    startup = result.scalar_one_or_none()
    if startup is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")
    return startup


async def require_startup_owner(
    startup: Startup = Depends(get_startup_or_404),
    current_user: User = Depends(get_current_user),
) -> Startup:
    if startup.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the startup owner")
    return startup


async def require_startup_access(
    startup: Startup = Depends(get_startup_or_404),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Startup:
    if startup.created_by == current_user.id:
        return startup
    result = await db.execute(
        select(StartupMember).where(
            StartupMember.startup_id == startup.id,
            StartupMember.user_id == current_user.id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to this startup")
    return startup
