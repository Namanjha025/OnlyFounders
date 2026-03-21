"""Marketplace business logic: profile scoring, onboarding steps, view serialization."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.models.marketplace_profile import (
    AdvisorProfile,
    FounderMarketplaceProfile,
    MarketplaceProfile,
    ProfessionalProfile,
)


# ── Profile scoring ────────────────────────────────────────────────

BASE_FIELD_WEIGHTS = {
    "headline": 8,
    "bio": 8,
    "avatar_url": 5,
    "location": 4,
    "skills": 8,
    "linkedin_url": 4,
    "website_url": 3,
}

PROFESSIONAL_FIELD_WEIGHTS = {
    "primary_role": 10,
    "years_experience": 8,
    "availability_status": 8,
    "service_offerings": 12,
    "certifications": 7,
    "hourly_rate": 5,
    "portfolio_url": 5,
    "cal_booking_link": 5,
}

ADVISOR_FIELD_WEIGHTS = {
    "domain_expertise": 12,
    "investment_thesis": 10,
    "portfolio_companies": 8,
    "investment_stages": 5,
    "check_size_min": 5,
    "check_size_max": 5,
    "fee_structure": 5,
    "availability": 5,
    "cal_booking_link": 5,
}

FOUNDER_FIELD_WEIGHTS = {
    "startup_id": 12,
    "looking_for_roles": 10,
    "cofounder_brief": 10,
    "startup_stage": 5,
    "industry": 5,
    "commitment_level": 5,
    "equity_offered": 5,
    "remote_ok": 3,
    "funding_stage": 5,
}


def _field_filled(obj: object, field: str) -> bool:
    val = getattr(obj, field, None)
    if val is None:
        return False
    if isinstance(val, (list, dict)):
        return bool(val)
    if isinstance(val, str):
        return bool(val.strip())
    return True


def calculate_profile_score(
    profile: MarketplaceProfile,
    type_profile: Optional[object] = None,
) -> int:
    score = 0

    # Base fields
    for field, weight in BASE_FIELD_WEIGHTS.items():
        if _field_filled(profile, field):
            score += weight

    # Type-specific fields
    if type_profile is None:
        type_profile = profile.type_profile

    if type_profile is not None:
        if isinstance(type_profile, ProfessionalProfile):
            weights = PROFESSIONAL_FIELD_WEIGHTS
        elif isinstance(type_profile, AdvisorProfile):
            weights = ADVISOR_FIELD_WEIGHTS
        elif isinstance(type_profile, FounderMarketplaceProfile):
            weights = FOUNDER_FIELD_WEIGHTS
        else:
            weights = {}

        for field, weight in weights.items():
            if _field_filled(type_profile, field):
                score += weight

    return min(score, 100)


# ── Onboarding steps ───────────────────────────────────────────────

PROFESSIONAL_STEPS = {
    1: {"name": "Basics", "fields": ["headline", "bio", "avatar_url", "location"]},
    2: {"name": "Skills", "fields": ["skills", "primary_role", "years_experience", "certifications"]},
    3: {"name": "Services", "fields": ["service_offerings", "hourly_rate", "availability_status", "employment_type_preference"]},
    4: {"name": "Links", "fields": ["linkedin_url", "website_url", "portfolio_url", "cal_booking_link"]},
}

ADVISOR_STEPS = {
    1: {"name": "Basics", "fields": ["headline", "bio", "avatar_url", "location"]},
    2: {"name": "Expertise", "fields": ["skills", "domain_expertise", "investment_thesis"]},
    3: {"name": "Investment", "fields": ["investment_stages", "portfolio_companies", "check_size_min", "check_size_max", "fee_structure"]},
    4: {"name": "Availability", "fields": ["availability", "cal_booking_link", "linkedin_url", "website_url"]},
}

FOUNDER_STEPS = {
    1: {"name": "Basics", "fields": ["headline", "bio", "avatar_url", "location"]},
    2: {"name": "Startup", "fields": ["startup_stage", "industry", "funding_stage"]},
    3: {"name": "Co-founder", "fields": ["looking_for_roles", "cofounder_brief", "equity_offered", "commitment_level", "remote_ok"]},
    4: {"name": "Links", "fields": ["skills", "linkedin_url", "website_url"]},
}

STEPS_BY_TYPE = {
    "professional": PROFESSIONAL_STEPS,
    "advisor": ADVISOR_STEPS,
    "founder": FOUNDER_STEPS,
}

# Fields that live on the base profile vs. the type-specific table
BASE_PROFILE_FIELDS = {
    "headline", "bio", "avatar_url", "location", "skills",
    "linkedin_url", "website_url",
}


def get_onboarding_steps(profile_type: str) -> Dict[int, Dict]:
    return STEPS_BY_TYPE.get(profile_type, {})


def get_completed_steps(profile: MarketplaceProfile) -> List[int]:
    extra = profile.extra_data or {}
    onboarding = extra.get("onboarding", {})
    return onboarding.get("completed_steps", [])


def mark_step_complete(profile: MarketplaceProfile, step: int) -> None:
    extra = dict(profile.extra_data or {})
    onboarding = dict(extra.get("onboarding", {}))
    completed = list(onboarding.get("completed_steps", []))
    if step not in completed:
        completed.append(step)
        completed.sort()
    onboarding["completed_steps"] = completed
    extra["onboarding"] = onboarding
    profile.extra_data = extra


def apply_step_data(
    profile: MarketplaceProfile,
    type_profile: object,
    step: int,
    data: Dict[str, Any],
) -> None:
    steps = get_onboarding_steps(profile.profile_type)
    if step not in steps:
        raise ValueError(f"Invalid step {step} for {profile.profile_type}")

    allowed_fields = set(steps[step]["fields"])

    for field, value in data.items():
        if field not in allowed_fields:
            continue

        if field in BASE_PROFILE_FIELDS:
            setattr(profile, field, value)
        else:
            if type_profile is not None:
                setattr(type_profile, field, value)

    # Sync skills_text for FTS trigger
    if "skills" in data and data["skills"]:
        skills = data["skills"]
        if isinstance(skills, list):
            profile.skills_text = ", ".join(str(s) for s in skills)

    mark_step_complete(profile, step)
