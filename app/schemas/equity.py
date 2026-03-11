from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EquityShareholderCreate(BaseModel):
    name: str
    relationship_type: Optional[str] = None
    equity_percentage: Optional[float] = None
    share_class: Optional[str] = None
    shares_owned: Optional[int] = None
    vesting_schedule: Optional[str] = None
    investment_amount: Optional[int] = None
    notes: Optional[str] = None


class EquityShareholderUpdate(BaseModel):
    name: Optional[str] = None
    relationship_type: Optional[str] = None
    equity_percentage: Optional[float] = None
    share_class: Optional[str] = None
    shares_owned: Optional[int] = None
    vesting_schedule: Optional[str] = None
    investment_amount: Optional[int] = None
    notes: Optional[str] = None


class EquityShareholderOut(BaseModel):
    id: uuid.UUID
    startup_id: uuid.UUID
    name: str
    relationship_type: Optional[str] = None
    equity_percentage: Optional[float] = None
    share_class: Optional[str] = None
    shares_owned: Optional[int] = None
    vesting_schedule: Optional[str] = None
    investment_amount: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
