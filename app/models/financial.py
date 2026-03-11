from __future__ import annotations

from typing import Optional

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import FundingRoundType


class FinancialDetail(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "financial_details"

    startup_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    monthly_burn_rate: Mapped[Optional[int]] = mapped_column(BigInteger)
    cash_in_bank: Mapped[Optional[int]] = mapped_column(BigInteger)
    runway_months: Mapped[Optional[int]] = mapped_column(Integer)
    monthly_revenue: Mapped[Optional[int]] = mapped_column(BigInteger)
    monthly_expenses: Mapped[Optional[int]] = mapped_column(BigInteger)
    gross_margin_pct: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    is_fundraising: Mapped[Optional[bool]] = mapped_column(Boolean)
    fundraise_target: Mapped[Optional[int]] = mapped_column(BigInteger)
    fundraise_round_type: Mapped[Optional[FundingRoundType]] = mapped_column(
        ENUM(FundingRoundType, name="fundingroundtype", create_type=True, values_callable=lambda e: [x.value for x in e])
    )
    total_raised: Mapped[Optional[int]] = mapped_column(BigInteger)

    startup = relationship("Startup", back_populates="financial_detail")
