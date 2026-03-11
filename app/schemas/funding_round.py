from __future__ import annotations

import datetime
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.models.enums import FundingRoundType


class FundingRoundCreate(BaseModel):
    round_type: FundingRoundType
    amount_raised: Optional[int] = None
    pre_money_valuation: Optional[int] = None
    post_money_valuation: Optional[int] = None
    round_date: Optional[datetime.date] = None
    lead_investor: Optional[str] = None
    investors: Optional[List[Dict[str, Any]]] = None
    instrument_type: Optional[str] = None
    notes: Optional[str] = None


class FundingRoundUpdate(BaseModel):
    round_type: Optional[FundingRoundType] = None
    amount_raised: Optional[int] = None
    pre_money_valuation: Optional[int] = None
    post_money_valuation: Optional[int] = None
    round_date: Optional[datetime.date] = None
    lead_investor: Optional[str] = None
    investors: Optional[List[Dict[str, Any]]] = None
    instrument_type: Optional[str] = None
    notes: Optional[str] = None


class FundingRoundOut(BaseModel):
    id: uuid.UUID
    startup_id: uuid.UUID
    round_type: FundingRoundType
    amount_raised: Optional[int] = None
    pre_money_valuation: Optional[int] = None
    post_money_valuation: Optional[int] = None
    round_date: Optional[datetime.date] = None
    lead_investor: Optional[str] = None
    investors: Optional[List[Dict[str, Any]]] = None
    instrument_type: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
