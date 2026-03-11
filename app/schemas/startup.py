from __future__ import annotations

import datetime
import uuid
from typing import Optional

from pydantic import BaseModel

from app.models.enums import (
    Industry,
    StartupStage,
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
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    stage: Optional[StartupStage] = None
    industry: Optional[Industry] = None
    founded_date: Optional[datetime.date] = None
    hq_city: Optional[str] = None
    hq_country: Optional[str] = None
    is_remote: Optional[bool] = None
    team_size: Optional[int] = None


class StartupOut(BaseModel):
    id: uuid.UUID
    created_by: uuid.UUID
    name: str
    slug: str
    tagline: Optional[str] = None
    short_description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    stage: Optional[StartupStage] = None
    industry: Optional[Industry] = None
    founded_date: Optional[datetime.date] = None
    hq_city: Optional[str] = None
    hq_country: Optional[str] = None
    is_remote: Optional[bool] = None
    team_size: Optional[int] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
