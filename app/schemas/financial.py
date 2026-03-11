from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.enums import FundingRoundType


class FinancialDetailUpdate(BaseModel):
    monthly_burn_rate: Optional[int] = None
    cash_in_bank: Optional[int] = None
    runway_months: Optional[int] = None
    monthly_revenue: Optional[int] = None
    monthly_expenses: Optional[int] = None
    gross_margin_pct: Optional[float] = None
    is_fundraising: Optional[bool] = None
    fundraise_target: Optional[int] = None
    fundraise_round_type: Optional[FundingRoundType] = None
    total_raised: Optional[int] = None


class FinancialDetailOut(BaseModel):
    id: uuid.UUID
    startup_id: uuid.UUID
    monthly_burn_rate: Optional[int] = None
    cash_in_bank: Optional[int] = None
    runway_months: Optional[int] = None
    monthly_revenue: Optional[int] = None
    monthly_expenses: Optional[int] = None
    gross_margin_pct: Optional[float] = None
    is_fundraising: Optional[bool] = None
    fundraise_target: Optional[int] = None
    fundraise_round_type: Optional[FundingRoundType] = None
    total_raised: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
