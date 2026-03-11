from __future__ import annotations

from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, Text
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import ProductStage


class ProductDetail(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "product_details"

    startup_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    problem: Mapped[Optional[str]] = mapped_column(Text)
    solution: Mapped[Optional[str]] = mapped_column(Text)
    product_stage: Mapped[Optional[ProductStage]] = mapped_column(
        ENUM(ProductStage, name="productstage", create_type=True, values_callable=lambda e: [x.value for x in e])
    )
    why_now: Mapped[Optional[str]] = mapped_column(Text)
    unique_insight: Mapped[Optional[str]] = mapped_column(Text)
    target_audience: Mapped[Optional[str]] = mapped_column(Text)
    tam: Mapped[Optional[int]] = mapped_column(BigInteger)
    sam: Mapped[Optional[int]] = mapped_column(BigInteger)
    som: Mapped[Optional[int]] = mapped_column(BigInteger)
    competitors: Mapped[Optional[dict]] = mapped_column(JSONB)
    competitive_advantage: Mapped[Optional[str]] = mapped_column(Text)
    revenue_model: Mapped[Optional[str]] = mapped_column(Text)
    tech_stack: Mapped[Optional[dict]] = mapped_column(JSONB)
    go_to_market: Mapped[Optional[str]] = mapped_column(Text)

    startup = relationship("Startup", back_populates="product_detail")
