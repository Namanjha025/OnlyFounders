from __future__ import annotations

import datetime
import uuid
from typing import List, Optional

from pydantic import BaseModel

from app.models.enums import (
    BusinessModel,
    IncorporationType,
    Industry,
    StartupStage,
    TargetMarket,
)


class StartupCreate(BaseModel):
    name: str
    tagline: Optional[str] = None
    short_description: Optional[str] = None
    stage: Optional[StartupStage] = None
    industry: Optional[Industry] = None


class StartupUpdate(BaseModel):
    name: Optional[str] = None
    tagline: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    demo_url: Optional[str] = None
    stage: Optional[StartupStage] = None
    industry: Optional[Industry] = None
    industries: Optional[List[str]] = None
    business_model: Optional[BusinessModel] = None
    target_market: Optional[TargetMarket] = None
    founded_date: Optional[datetime.date] = None
    is_incorporated: Optional[bool] = None
    entity_type: Optional[IncorporationType] = None
    incorporation_country: Optional[str] = None
    incorporation_state: Optional[str] = None
    legal_entity_name: Optional[str] = None
    hq_city: Optional[str] = None
    hq_country: Optional[str] = None
    is_remote: Optional[bool] = None
    company_linkedin: Optional[str] = None
    company_twitter: Optional[str] = None
    team_size: Optional[int] = None


class StartupOut(BaseModel):
    id: uuid.UUID
    created_by: uuid.UUID
    name: str
    slug: str
    tagline: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    demo_url: Optional[str] = None
    stage: Optional[StartupStage] = None
    industry: Optional[Industry] = None
    industries: Optional[List[str]] = None
    business_model: Optional[BusinessModel] = None
    target_market: Optional[TargetMarket] = None
    founded_date: Optional[datetime.date] = None
    is_incorporated: Optional[bool] = None
    entity_type: Optional[IncorporationType] = None
    incorporation_country: Optional[str] = None
    incorporation_state: Optional[str] = None
    legal_entity_name: Optional[str] = None
    hq_city: Optional[str] = None
    hq_country: Optional[str] = None
    is_remote: Optional[bool] = None
    company_linkedin: Optional[str] = None
    company_twitter: Optional[str] = None
    team_size: Optional[int] = None
    profile_completeness: int = 0
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
