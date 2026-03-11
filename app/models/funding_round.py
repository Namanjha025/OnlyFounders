from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import BigInteger, Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import FundingRoundType


class FundingRound(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "funding_rounds"

    startup_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    round_type: Mapped[FundingRoundType] = mapped_column(
        ENUM(FundingRoundType, name="fundingroundtype", create_type=True, values_callable=lambda e: [x.value for x in e]), nullable=False
    )
    amount_raised: Mapped[Optional[int]] = mapped_column(BigInteger)
    pre_money_valuation: Mapped[Optional[int]] = mapped_column(BigInteger)
    post_money_valuation: Mapped[Optional[int]] = mapped_column(BigInteger)
    round_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    lead_investor: Mapped[Optional[str]] = mapped_column(String(200))
    investors: Mapped[Optional[dict]] = mapped_column(JSONB)
    instrument_type: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    startup = relationship("Startup", back_populates="funding_rounds")
