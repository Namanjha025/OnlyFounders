from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.startup import require_startup_access
from app.models.startup import Startup
from app.models.traction import TractionMetric
from app.schemas.traction import TractionMetricOut, TractionMetricUpdate

router = APIRouter(prefix="/api/v1/startups/{startup_id}/traction", tags=["traction"])


@router.get("/", response_model=TractionMetricOut)
async def get_traction(
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TractionMetric).where(TractionMetric.startup_id == startup.id)
    )
    metric = result.scalar_one_or_none()
    if not metric:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Traction metrics not found")
    return TractionMetricOut.model_validate(metric)


@router.put("/", response_model=TractionMetricOut)
async def upsert_traction(
    data: TractionMetricUpdate,
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TractionMetric).where(TractionMetric.startup_id == startup.id)
    )
    metric = result.scalar_one_or_none()
    update_data = data.model_dump(exclude_unset=True)

    if metric is None:
        metric = TractionMetric(startup_id=startup.id, **update_data)
        db.add(metric)
    else:
        for key, value in update_data.items():
            setattr(metric, key, value)

    await db.commit()
    await db.refresh(metric)
    return TractionMetricOut.model_validate(metric)
