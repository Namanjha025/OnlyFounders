from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class FounderProfileUpdate(BaseModel):
    phone: Optional[str] = None
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    profile_photo_url: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    is_technical: Optional[bool] = None
    is_full_time: Optional[bool] = None
    education: Optional[str] = None
    degree_field: Optional[str] = None
    years_of_experience: Optional[int] = None
    previous_startups: Optional[str] = None
    notable_achievement: Optional[str] = None
    skills: Optional[List[str]] = None
    domain_expertise: Optional[List[str]] = None


class FounderProfileOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    phone: Optional[str] = None
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    profile_photo_url: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    is_technical: Optional[bool] = None
    is_full_time: Optional[bool] = None
    education: Optional[str] = None
    degree_field: Optional[str] = None
    years_of_experience: Optional[int] = None
    previous_startups: Optional[str] = None
    notable_achievement: Optional[str] = None
    skills: Optional[List[str]] = None
    domain_expertise: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
