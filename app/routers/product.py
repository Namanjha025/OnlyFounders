from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.startup import require_startup_access
from app.models.product import ProductDetail
from app.models.startup import Startup
from app.models.user import User
from app.schemas.product import ProductDetailOut, ProductDetailUpdate

router = APIRouter(prefix="/api/v1/startups/{startup_id}/product", tags=["product"])


@router.get("/", response_model=ProductDetailOut)
async def get_product(
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ProductDetail).where(ProductDetail.startup_id == startup.id)
    )
    detail = result.scalar_one_or_none()
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product details not found")
    return ProductDetailOut.model_validate(detail)


@router.put("/", response_model=ProductDetailOut)
async def upsert_product(
    data: ProductDetailUpdate,
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ProductDetail).where(ProductDetail.startup_id == startup.id)
    )
    detail = result.scalar_one_or_none()
    update_data = data.model_dump(exclude_unset=True)

    if detail is None:
        detail = ProductDetail(startup_id=startup.id, **update_data)
        db.add(detail)
    else:
        for key, value in update_data.items():
            setattr(detail, key, value)

    await db.commit()
    await db.refresh(detail)
    return ProductDetailOut.model_validate(detail)
