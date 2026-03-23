from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ── Type-specific input data ───────────────────────────────────────


class ProfessionalProfileData(BaseModel):
    primary_role: Optional[str] = None
    years_experience: Optional[int] = None
    hourly_rate: Optional[float] = None
    availability_status: Optional[str] = None
    employment_type_preference: Optional[List[str]] = None
    portfolio_url: Optional[str] = None
    certifications: Optional[List[Any]] = None
    service_offerings: Optional[List[Any]] = None
    cal_booking_link: Optional[str] = None


class AdvisorProfileData(BaseModel):
    domain_expertise: Optional[List[str]] = None
    investment_thesis: Optional[str] = None
    portfolio_companies: Optional[List[Any]] = None
    investment_stages: Optional[List[str]] = None
    check_size_min: Optional[float] = None
    check_size_max: Optional[float] = None
    fee_structure: Optional[str] = None
    availability: Optional[str] = None
    cal_booking_link: Optional[str] = None


class FounderProfileData(BaseModel):
    startup_id: Optional[uuid.UUID] = None
    looking_for_roles: Optional[List[str]] = None
    equity_offered: Optional[str] = None
    startup_stage: Optional[str] = None
    industry: Optional[str] = None
    cofounder_brief: Optional[str] = None
    commitment_level: Optional[str] = None
    remote_ok: Optional[bool] = None
    funding_stage: Optional[str] = None


# ── Profile Create / Update ────────────────────────────────────────


class MarketplaceProfileCreate(BaseModel):
    profile_type: Literal["founder", "professional", "advisor"]
    headline: str = Field(max_length=500)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = Field(default_factory=list, max_length=30)
    linkedin_url: Optional[str] = None
    website_url: Optional[str] = None
    is_public: bool = False
    professional_data: Optional[ProfessionalProfileData] = None
    advisor_data: Optional[AdvisorProfileData] = None
    founder_data: Optional[FounderProfileData] = None


class MarketplaceProfileUpdate(BaseModel):
    headline: Optional[str] = Field(default=None, max_length=500)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    linkedin_url: Optional[str] = None
    website_url: Optional[str] = None


class TypeDataUpdate(BaseModel):
    professional_data: Optional[ProfessionalProfileData] = None
    advisor_data: Optional[AdvisorProfileData] = None
    founder_data: Optional[FounderProfileData] = None


# ── Profile Output Views ──────────────────────────────────────────


class ProfilePublicView(BaseModel):
    id: uuid.UUID
    profile_type: str
    headline: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    profile_score: int = 0
    availability_status: Optional[str] = None
    primary_role: Optional[str] = None

    model_config = {"from_attributes": True}


class ProfessionalProfileOut(BaseModel):
    primary_role: Optional[str] = None
    years_experience: Optional[int] = None
    hourly_rate: Optional[float] = None
    availability_status: Optional[str] = None
    employment_type_preference: Optional[List[str]] = None
    portfolio_url: Optional[str] = None
    certifications: Optional[List[Any]] = None
    service_offerings: Optional[List[Any]] = None
    cal_booking_link: Optional[str] = None

    model_config = {"from_attributes": True}


class AdvisorProfileOut(BaseModel):
    domain_expertise: Optional[List[str]] = None
    investment_thesis: Optional[str] = None
    portfolio_companies: Optional[List[Any]] = None
    investment_stages: Optional[List[str]] = None
    check_size_min: Optional[float] = None
    check_size_max: Optional[float] = None
    fee_structure: Optional[str] = None
    availability: Optional[str] = None
    cal_booking_link: Optional[str] = None

    model_config = {"from_attributes": True}


class FounderProfileOut(BaseModel):
    startup_id: Optional[uuid.UUID] = None
    looking_for_roles: Optional[List[str]] = None
    equity_offered: Optional[str] = None
    startup_stage: Optional[str] = None
    industry: Optional[str] = None
    cofounder_brief: Optional[str] = None
    commitment_level: Optional[str] = None
    remote_ok: Optional[bool] = None
    funding_stage: Optional[str] = None

    model_config = {"from_attributes": True}


class ProfileDocumentOut(BaseModel):
    id: uuid.UUID
    document_type: Optional[str] = None
    title: str
    s3_url: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    is_public: bool = True
    sort_order: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileSelfView(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    profile_type: str
    headline: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    linkedin_url: Optional[str] = None
    website_url: Optional[str] = None
    profile_score: int = 0
    is_public: bool = False
    visibility_settings: Optional[Dict[str, Any]] = None
    extra_data: Optional[Dict[str, Any]] = None
    profile_views: int = 0
    professional_data: Optional[ProfessionalProfileOut] = None
    advisor_data: Optional[AdvisorProfileOut] = None
    founder_data: Optional[FounderProfileOut] = None
    documents: Optional[List[ProfileDocumentOut]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Onboarding ─────────────────────────────────────────────────────


class OnboardingStartRequest(BaseModel):
    profile_type: Literal["founder", "professional", "advisor"]


class OnboardingStepUpdate(BaseModel):
    data: Dict[str, Any]


class OnboardingStatusOut(BaseModel):
    profile_id: uuid.UUID
    profile_type: str
    current_step: int
    total_steps: int = 4
    completed_steps: List[int]
    profile_score: int
    is_complete: bool

    model_config = {"from_attributes": True}


# ── Documents ──────────────────────────────────────────────────────


class ProfileDocUploadURLRequest(BaseModel):
    file_name: str
    document_type: Optional[str] = None
    mime_type: str = "application/octet-stream"


class ProfileDocUploadURLResponse(BaseModel):
    upload_url: str
    s3_key: str


class ProfileDocConfirmRequest(BaseModel):
    s3_key: str
    title: str
    document_type: Optional[str] = None
    file_name: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    is_public: bool = True


# ── Visibility ─────────────────────────────────────────────────────


class VisibilitySettings(BaseModel):
    is_public: bool = False
    show_email: bool = False
    show_phone: bool = False
    show_linkedin: bool = True
    show_location: bool = True
    discoverable_in_search: bool = True


class VisibilityUpdate(BaseModel):
    is_public: Optional[bool] = None
    show_email: Optional[bool] = None
    show_phone: Optional[bool] = None
    show_linkedin: Optional[bool] = None
    show_location: Optional[bool] = None
    discoverable_in_search: Optional[bool] = None


# ── Phase 2: Discovery & Search ───────────────────────────────────


class FacetBucket(BaseModel):
    value: str
    count: int


class FacetResponse(BaseModel):
    profile_types: List[FacetBucket] = []
    skills: List[FacetBucket] = []
    availability: List[FacetBucket] = []
    hourly_rate_ranges: List[FacetBucket] = []
    locations: List[FacetBucket] = []


class PaginatedProfileResponse(BaseModel):
    items: List[ProfilePublicView]
    total: int
    page: int
    page_size: int
    total_pages: int
    facets: Optional[FacetResponse] = None
