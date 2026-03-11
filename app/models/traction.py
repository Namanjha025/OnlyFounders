from __future__ import annotations

from typing import Optional

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class TractionMetric(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "traction_metrics"

    startup_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    has_users: Mapped[Optional[bool]] = mapped_column(Boolean)
    active_users: Mapped[Optional[int]] = mapped_column(Integer)
    total_registered_users: Mapped[Optional[int]] = mapped_column(Integer)
    paying_customers: Mapped[Optional[int]] = mapped_column(Integer)
    user_growth_rate_pct: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    churn_rate_pct: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    has_revenue: Mapped[Optional[bool]] = mapped_column(Boolean)
    mrr: Mapped[Optional[int]] = mapped_column(BigInteger)
    arr: Mapped[Optional[int]] = mapped_column(BigInteger)
    revenue_growth_rate_pct: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    north_star_metric_name: Mapped[Optional[str]] = mapped_column(String(100))
    north_star_metric_value: Mapped[Optional[str]] = mapped_column(String(100))
    ltv_cents: Mapped[Optional[int]] = mapped_column(BigInteger)
    cac_cents: Mapped[Optional[int]] = mapped_column(BigInteger)
    key_milestones: Mapped[Optional[str]] = mapped_column(Text)
    next_milestones: Mapped[Optional[str]] = mapped_column(Text)

    startup = relationship("Startup", back_populates="traction_metric")
