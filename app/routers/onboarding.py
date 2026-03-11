from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.startup import require_startup_access
from app.models.document import Document
from app.models.financial import FinancialDetail
from app.models.founder_profile import FounderProfile
from app.models.product import ProductDetail
from app.models.startup import Startup
from app.models.startup_member import StartupMember
from app.models.traction import TractionMetric
from app.models.user import User
from app.schemas.onboarding import OnboardingStatus, SectionStatus

router = APIRouter(prefix="/api/v1/startups/{startup_id}/onboarding", tags=["onboarding"])

FOUNDER_FIELDS = [
    "phone", "bio", "linkedin_url", "city", "country",
    "is_technical", "is_full_time", "education", "years_of_experience",
    "notable_achievement", "skills",
]

COMPANY_FIELDS = [
    "name", "tagline", "short_description", "stage", "industry",
    "business_model", "target_market", "founded_date",
    "is_incorporated", "hq_city", "hq_country",
]

PRODUCT_FIELDS = [
    "problem", "solution", "product_stage", "target_audience",
    "tam", "competitive_advantage", "revenue_model",
]

TRACTION_FIELDS = [
    "has_users", "has_revenue", "north_star_metric_name",
    "key_milestones",
]

FINANCIAL_FIELDS = [
    "monthly_burn_rate", "cash_in_bank", "runway_months",
    "is_fundraising", "total_raised",
]


def _calc_completeness(obj: object, fields: List[str]) -> int:
    if obj is None:
        return 0
    filled = sum(1 for f in fields if getattr(obj, f, None) is not None)
    return int((filled / len(fields)) * 100) if fields else 0


@router.get("/", response_model=OnboardingStatus)
async def get_onboarding_status(
    startup: Startup = Depends(require_startup_access),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Founder profile
    fp_result = await db.execute(
        select(FounderProfile).where(FounderProfile.user_id == current_user.id)
    )
    founder_profile = fp_result.scalar_one_or_none()
    founder_pct = _calc_completeness(founder_profile, FOUNDER_FIELDS)

    # Company basics
    company_pct = _calc_completeness(startup, COMPANY_FIELDS)

    # Team
    member_result = await db.execute(
        select(func.count()).select_from(StartupMember).where(StartupMember.startup_id == startup.id)
    )
    member_count = member_result.scalar() or 0
    team_pct = min(100, member_count * 50)  # 1 member = 50%, 2+ = 100%

    # Product
    pd_result = await db.execute(
        select(ProductDetail).where(ProductDetail.startup_id == startup.id)
    )
    product = pd_result.scalar_one_or_none()
    product_pct = _calc_completeness(product, PRODUCT_FIELDS)

    # Traction
    tm_result = await db.execute(
        select(TractionMetric).where(TractionMetric.startup_id == startup.id)
    )
    traction = tm_result.scalar_one_or_none()
    traction_pct = _calc_completeness(traction, TRACTION_FIELDS)

    # Financials
    fd_result = await db.execute(
        select(FinancialDetail).where(FinancialDetail.startup_id == startup.id)
    )
    financials = fd_result.scalar_one_or_none()
    financials_pct = _calc_completeness(financials, FINANCIAL_FIELDS)

    # Documents
    doc_result = await db.execute(
        select(func.count()).select_from(Document).where(Document.startup_id == startup.id)
    )
    doc_count = doc_result.scalar() or 0
    documents_pct = min(100, doc_count * 50)  # 1 doc = 50%, 2+ = 100%

    sections = {
        "founder_profile": SectionStatus(complete=founder_pct >= 60, completeness=founder_pct),
        "company_basics": SectionStatus(complete=company_pct >= 60, completeness=company_pct),
        "team": SectionStatus(complete=team_pct >= 50, completeness=team_pct),
        "product": SectionStatus(complete=product_pct >= 60, completeness=product_pct),
        "traction": SectionStatus(complete=traction_pct >= 50, completeness=traction_pct),
        "financials": SectionStatus(complete=financials_pct >= 50, completeness=financials_pct),
        "documents": SectionStatus(complete=documents_pct >= 50, completeness=documents_pct),
    }

    overall = int(sum(s.completeness for s in sections.values()) / len(sections))

    return OnboardingStatus(overall_completeness=overall, sections=sections)
