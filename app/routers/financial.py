from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.startup import require_startup_access
from app.models.financial import FinancialDetail
from app.models.startup import Startup
from app.schemas.financial import FinancialDetailOut, FinancialDetailUpdate

router = APIRouter(prefix="/api/v1/startups/{startup_id}/financials", tags=["financials"])


@router.get("/", response_model=FinancialDetailOut)
async def get_financials(
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FinancialDetail).where(FinancialDetail.startup_id == startup.id)
    )
    detail = result.scalar_one_or_none()
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Financial details not found")
    return FinancialDetailOut.model_validate(detail)


@router.put("/", response_model=FinancialDetailOut)
async def upsert_financials(
    data: FinancialDetailUpdate,
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FinancialDetail).where(FinancialDetail.startup_id == startup.id)
    )
    detail = result.scalar_one_or_none()
    update_data = data.model_dump(exclude_unset=True)

    if detail is None:
        detail = FinancialDetail(startup_id=startup.id, **update_data)
        db.add(detail)
    else:
        for key, value in update_data.items():
            setattr(detail, key, value)

    await db.commit()
    await db.refresh(detail)
    return FinancialDetailOut.model_validate(detail)
