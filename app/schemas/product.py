from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.models.enums import ProductStage


class ProductDetailUpdate(BaseModel):
    problem: Optional[str] = None
    solution: Optional[str] = None
    product_stage: Optional[ProductStage] = None
    why_now: Optional[str] = None
    unique_insight: Optional[str] = None
    target_audience: Optional[str] = None
    tam: Optional[int] = None
    sam: Optional[int] = None
    som: Optional[int] = None
    competitors: Optional[List[Dict[str, Any]]] = None
    competitive_advantage: Optional[str] = None
    revenue_model: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    go_to_market: Optional[str] = None


class ProductDetailOut(BaseModel):
    id: uuid.UUID
    startup_id: uuid.UUID
    problem: Optional[str] = None
    solution: Optional[str] = None
    product_stage: Optional[ProductStage] = None
    why_now: Optional[str] = None
    unique_insight: Optional[str] = None
    target_audience: Optional[str] = None
    tam: Optional[int] = None
    sam: Optional[int] = None
    som: Optional[int] = None
    competitors: Optional[List[Dict[str, Any]]] = None
    competitive_advantage: Optional[str] = None
    revenue_model: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    go_to_market: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
