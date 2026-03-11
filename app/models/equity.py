from __future__ import annotations

from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class EquityShareholder(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "equity_shareholders"

    startup_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    relationship_type: Mapped[Optional[str]] = mapped_column(String(50))
    equity_percentage: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    share_class: Mapped[Optional[str]] = mapped_column(String(50))
    shares_owned: Mapped[Optional[int]] = mapped_column(Integer)
    vesting_schedule: Mapped[Optional[str]] = mapped_column(String(200))
    investment_amount: Mapped[Optional[int]] = mapped_column(BigInteger)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    startup = relationship("Startup", back_populates="equity_shareholders")
