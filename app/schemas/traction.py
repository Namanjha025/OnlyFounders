from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TractionMetricUpdate(BaseModel):
    has_users: Optional[bool] = None
    active_users: Optional[int] = None
    total_registered_users: Optional[int] = None
    paying_customers: Optional[int] = None
    user_growth_rate_pct: Optional[float] = None
    churn_rate_pct: Optional[float] = None
    has_revenue: Optional[bool] = None
    mrr: Optional[int] = None
    arr: Optional[int] = None
    revenue_growth_rate_pct: Optional[float] = None
    north_star_metric_name: Optional[str] = None
    north_star_metric_value: Optional[str] = None
    ltv_cents: Optional[int] = None
    cac_cents: Optional[int] = None
    key_milestones: Optional[str] = None
    next_milestones: Optional[str] = None


class TractionMetricOut(BaseModel):
    id: uuid.UUID
    startup_id: uuid.UUID
    has_users: Optional[bool] = None
    active_users: Optional[int] = None
    total_registered_users: Optional[int] = None
    paying_customers: Optional[int] = None
    user_growth_rate_pct: Optional[float] = None
    churn_rate_pct: Optional[float] = None
    has_revenue: Optional[bool] = None
    mrr: Optional[int] = None
    arr: Optional[int] = None
    revenue_growth_rate_pct: Optional[float] = None
    north_star_metric_name: Optional[str] = None
    north_star_metric_value: Optional[str] = None
    ltv_cents: Optional[int] = None
    cac_cents: Optional[int] = None
    key_milestones: Optional[str] = None
    next_milestones: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
