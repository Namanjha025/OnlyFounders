from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.marketplace import (
    get_marketplace_profile_or_404,
    get_my_marketplace_profile,
)
from app.models.marketplace_profile import (
    AdvisorProfile,
    FounderMarketplaceProfile,
    MarketplaceProfile,
    ProfessionalProfile,
    ProfileDocument,
)
from app.models.user import User
from app.schemas.marketplace_profile import (
    AdvisorProfileOut,
    FounderProfileOut,
    MarketplaceProfileCreate,
    MarketplaceProfileUpdate,
    OnboardingStartRequest,
    OnboardingStatusOut,
    OnboardingStepUpdate,
    ProfileDocConfirmRequest,
    ProfileDocumentOut,
    ProfileDocUploadURLRequest,
    ProfileDocUploadURLResponse,
    ProfilePublicView,
    ProfileSelfView,
    ProfessionalProfileOut,
    TypeDataUpdate,
    VisibilitySettings,
    VisibilityUpdate,
)
from app.services.marketplace import (
    apply_step_data,
    calculate_profile_score,
    get_completed_steps,
    get_onboarding_steps,
)
from app.services.s3 import generate_upload_presigned_url

from sqlalchemy import or_, func as sa_func

router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])


# ── Helpers ────────────────────────────────────────────────────────


def _build_self_view(profile: MarketplaceProfile) -> dict:
    data = {
        "id": profile.id,
        "user_id": profile.user_id,
        "profile_type": profile.profile_type,
        "headline": profile.headline,
        "bio": profile.bio,
        "avatar_url": profile.avatar_url,
        "location": profile.location,
        "skills": profile.skills,
        "linkedin_url": profile.linkedin_url,
        "website_url": profile.website_url,
        "profile_score": profile.profile_score,
        "is_public": profile.is_public,
        "visibility_settings": profile.visibility_settings,
        "extra_data": profile.extra_data,
        "profile_views": profile.profile_views,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
        "professional_data": None,
        "advisor_data": None,
        "founder_data": None,
        "documents": [],
    }

    tp = profile.type_profile
    if isinstance(tp, ProfessionalProfile):
        data["professional_data"] = ProfessionalProfileOut.model_validate(tp).model_dump()
    elif isinstance(tp, AdvisorProfile):
        data["advisor_data"] = AdvisorProfileOut.model_validate(tp).model_dump()
    elif isinstance(tp, FounderMarketplaceProfile):
        data["founder_data"] = FounderProfileOut.model_validate(tp).model_dump()

    data["documents"] = [
        ProfileDocumentOut.model_validate(d).model_dump()
        for d in (profile.documents or [])
    ]
    return data


def _build_public_view(profile: MarketplaceProfile) -> dict:
    bio = profile.bio
    if bio and len(bio) > 200:
        bio = bio[:200] + "..."

    result = {
        "id": profile.id,
        "profile_type": profile.profile_type,
        "headline": profile.headline,
        "bio": bio,
        "avatar_url": profile.avatar_url,
        "location": profile.location,
        "skills": profile.skills,
        "profile_score": profile.profile_score,
        "primary_role": None,
        "availability_status": None,
    }

    tp = profile.type_profile
    if isinstance(tp, ProfessionalProfile):
        result["primary_role"] = tp.primary_role
        result["availability_status"] = tp.availability_status.value if tp.availability_status else None
    elif isinstance(tp, AdvisorProfile):
        result["availability_status"] = tp.availability

    return result


def _create_type_profile(profile_type: str, profile_id: uuid.UUID, data: dict | None):
    if profile_type == "professional":
        return ProfessionalProfile(
            profile_id=profile_id,
            **(data.model_dump(exclude_unset=True) if data else {}),
        )
    elif profile_type == "advisor":
        return AdvisorProfile(
            profile_id=profile_id,
            **(data.model_dump(exclude_unset=True) if data else {}),
        )
    elif profile_type == "founder":
        return FounderMarketplaceProfile(
            profile_id=profile_id,
            **(data.model_dump(exclude_unset=True) if data else {}),
        )
    return None


def _sync_skills_text(profile: MarketplaceProfile) -> None:
    if profile.skills and isinstance(profile.skills, list):
        profile.skills_text = ", ".join(str(s) for s in profile.skills)
    else:
        profile.skills_text = None


# ── Profile CRUD ───────────────────────────────────────────────────


@router.post("/profiles", response_model=ProfileSelfView, status_code=status.HTTP_201_CREATED)
async def create_profile(
    data: MarketplaceProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check for existing profile
    existing = await db.execute(
        select(MarketplaceProfile).where(MarketplaceProfile.user_id == current_user.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Profile already exists")

    # Create base profile
    profile = MarketplaceProfile(
        user_id=current_user.id,
        profile_type=data.profile_type,
        headline=data.headline,
        bio=data.bio,
        avatar_url=data.avatar_url,
        location=data.location,
        skills=data.skills or [],
        linkedin_url=data.linkedin_url,
        website_url=data.website_url,
        is_public=data.is_public,
    )
    _sync_skills_text(profile)
    db.add(profile)
    await db.flush()

    # Create type-specific profile
    type_data = (
        data.professional_data if data.profile_type == "professional"
        else data.advisor_data if data.profile_type == "advisor"
        else data.founder_data
    )
    type_profile = _create_type_profile(data.profile_type, profile.id, type_data)
    if type_profile:
        db.add(type_profile)
        await db.flush()

    # Calculate score
    profile.profile_score = calculate_profile_score(profile, type_profile)

    # Set marketplace_role on user
    from app.models.enums import MarketplaceRole
    current_user.marketplace_role = MarketplaceRole(data.profile_type)

    await db.commit()

    # Re-fetch with relationships
    result = await db.execute(
        select(MarketplaceProfile)
        .where(MarketplaceProfile.id == profile.id)
        .options(
            selectinload(MarketplaceProfile.professional_data),
            selectinload(MarketplaceProfile.advisor_data),
            selectinload(MarketplaceProfile.founder_data),
            selectinload(MarketplaceProfile.documents),
        )
    )
    profile = result.scalar_one()
    return ProfileSelfView(**_build_self_view(profile))


@router.get("/profiles/me", response_model=ProfileSelfView)
async def get_my_profile(
    profile: MarketplaceProfile = Depends(get_my_marketplace_profile),
):
    return ProfileSelfView(**_build_self_view(profile))


@router.get("/profiles/{profile_id}", response_model=None)
async def get_profile(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await get_marketplace_profile_or_404(profile_id, db)

    # Self view
    if profile.user_id == current_user.id:
        return ProfileSelfView(**_build_self_view(profile))

    # Public view — only if public
    if not profile.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    # Increment views (avoid race with SQL expression)
    await db.execute(
        MarketplaceProfile.__table__.update()
        .where(MarketplaceProfile.id == profile_id)
        .values(profile_views=MarketplaceProfile.profile_views + 1)
    )
    await db.commit()

    return ProfilePublicView(**_build_public_view(profile))


@router.patch("/profiles/me", response_model=ProfileSelfView)
async def update_my_profile(
    data: MarketplaceProfileUpdate,
    profile: MarketplaceProfile = Depends(get_my_marketplace_profile),
    db: AsyncSession = Depends(get_db),
):
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    _sync_skills_text(profile)
    profile.profile_score = calculate_profile_score(profile)
    await db.commit()
    await db.refresh(profile)

    # Re-fetch with relationships
    result = await db.execute(
        select(MarketplaceProfile)
        .where(MarketplaceProfile.id == profile.id)
        .options(
            selectinload(MarketplaceProfile.professional_data),
            selectinload(MarketplaceProfile.advisor_data),
            selectinload(MarketplaceProfile.founder_data),
            selectinload(MarketplaceProfile.documents),
        )
    )
    profile = result.scalar_one()
    return ProfileSelfView(**_build_self_view(profile))


@router.patch("/profiles/me/type-data", response_model=ProfileSelfView)
async def update_type_data(
    data: TypeDataUpdate,
    profile: MarketplaceProfile = Depends(get_my_marketplace_profile),
    db: AsyncSession = Depends(get_db),
):
    tp = profile.type_profile
    if tp is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No type profile found")

    # Determine which data to apply
    type_data = (
        data.professional_data if profile.profile_type == "professional"
        else data.advisor_data if profile.profile_type == "advisor"
        else data.founder_data
    )

    if type_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provide {profile.profile_type}_data field",
        )

    update_dict = type_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(tp, key, value)

    profile.profile_score = calculate_profile_score(profile, tp)
    await db.commit()

    # Re-fetch
    result = await db.execute(
        select(MarketplaceProfile)
        .where(MarketplaceProfile.id == profile.id)
        .options(
            selectinload(MarketplaceProfile.professional_data),
            selectinload(MarketplaceProfile.advisor_data),
            selectinload(MarketplaceProfile.founder_data),
            selectinload(MarketplaceProfile.documents),
        )
    )
    profile = result.scalar_one()
    return ProfileSelfView(**_build_self_view(profile))


@router.delete("/profiles/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_profile(
    profile: MarketplaceProfile = Depends(get_my_marketplace_profile),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user.marketplace_role = None
    await db.delete(profile)
    await db.commit()


# ── Onboarding ─────────────────────────────────────────────────────


@router.post("/onboarding/start", response_model=OnboardingStatusOut, status_code=status.HTTP_201_CREATED)
async def start_onboarding(
    data: OnboardingStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check existing
    existing = await db.execute(
        select(MarketplaceProfile).where(MarketplaceProfile.user_id == current_user.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Profile already exists")

    profile = MarketplaceProfile(
        user_id=current_user.id,
        profile_type=data.profile_type,
        is_public=False,
        extra_data={"onboarding": {"completed_steps": []}},
    )
    db.add(profile)
    await db.flush()

    # Create empty type profile
    type_profile = _create_type_profile(data.profile_type, profile.id, None)
    if type_profile:
        db.add(type_profile)

    # Set marketplace role
    from app.models.enums import MarketplaceRole
    current_user.marketplace_role = MarketplaceRole(data.profile_type)

    await db.commit()

    return OnboardingStatusOut(
        profile_id=profile.id,
        profile_type=profile.profile_type,
        current_step=1,
        total_steps=4,
        completed_steps=[],
        profile_score=0,
        is_complete=False,
    )


@router.patch("/onboarding/step/{step_number}", response_model=OnboardingStatusOut)
async def save_onboarding_step(
    step_number: int,
    body: OnboardingStepUpdate,
    profile: MarketplaceProfile = Depends(get_my_marketplace_profile),
    db: AsyncSession = Depends(get_db),
):
    steps = get_onboarding_steps(profile.profile_type)
    if step_number not in steps:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid step {step_number}. Valid steps: 1-{len(steps)}",
        )

    tp = profile.type_profile
    apply_step_data(profile, tp, step_number, body.data)

    profile.profile_score = calculate_profile_score(profile, tp)
    await db.commit()

    completed = get_completed_steps(profile)
    return OnboardingStatusOut(
        profile_id=profile.id,
        profile_type=profile.profile_type,
        current_step=max(completed) + 1 if completed and max(completed) < 4 else max(completed, default=1),
        total_steps=4,
        completed_steps=completed,
        profile_score=profile.profile_score,
        is_complete=len(completed) >= 4,
    )


@router.get("/onboarding/status", response_model=OnboardingStatusOut)
async def get_onboarding_status(
    profile: MarketplaceProfile = Depends(get_my_marketplace_profile),
):
    completed = get_completed_steps(profile)
    return OnboardingStatusOut(
        profile_id=profile.id,
        profile_type=profile.profile_type,
        current_step=max(completed) + 1 if completed and max(completed) < 4 else max(completed, default=1),
        total_steps=4,
        completed_steps=completed,
        profile_score=profile.profile_score,
        is_complete=len(completed) >= 4,
    )


# ── Documents ──────────────────────────────────────────────────────


@router.post("/profiles/me/documents/upload-url", response_model=ProfileDocUploadURLResponse)
async def get_upload_url(
    data: ProfileDocUploadURLRequest,
    profile: MarketplaceProfile = Depends(get_my_marketplace_profile),
):
    # Reuse S3 service with profile.id as the "startup_id" folder key
    result = generate_upload_presigned_url(
        file_name=data.file_name,
        mime_type=data.mime_type,
        startup_id=f"marketplace/{profile.id}",
    )
    return ProfileDocUploadURLResponse(upload_url=result["upload_url"], s3_key=result["s3_key"])


@router.post("/profiles/me/documents/confirm-upload", response_model=ProfileDocumentOut, status_code=status.HTTP_201_CREATED)
async def confirm_upload(
    data: ProfileDocConfirmRequest,
    profile: MarketplaceProfile = Depends(get_my_marketplace_profile),
    db: AsyncSession = Depends(get_db),
):
    doc = ProfileDocument(
        profile_id=profile.id,
        document_type=data.document_type,
        title=data.title,
        s3_key=data.s3_key,
        s3_url=data.s3_key,  # Will be replaced with CDN URL later
        file_size=data.file_size,
        mime_type=data.mime_type,
        is_public=data.is_public,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return ProfileDocumentOut.model_validate(doc)


@router.get("/profiles/me/documents", response_model=list[ProfileDocumentOut])
async def list_documents(
    profile: MarketplaceProfile = Depends(get_my_marketplace_profile),
):
    return [ProfileDocumentOut.model_validate(d) for d in (profile.documents or [])]


@router.delete("/profiles/me/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: uuid.UUID,
    profile: MarketplaceProfile = Depends(get_my_marketplace_profile),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ProfileDocument).where(
            ProfileDocument.id == doc_id,
            ProfileDocument.profile_id == profile.id,
        )
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    try:
        from app.services.s3 import delete_s3_object
        delete_s3_object(doc.s3_key)
    except Exception:
        pass

    await db.delete(doc)
    await db.commit()


# ── Visibility ─────────────────────────────────────────────────────


@router.get("/profiles/me/visibility", response_model=VisibilitySettings)
async def get_visibility(
    profile: MarketplaceProfile = Depends(get_my_marketplace_profile),
):
    settings = profile.visibility_settings or {}
    return VisibilitySettings(
        is_public=profile.is_public,
        show_email=settings.get("show_email", False),
        show_phone=settings.get("show_phone", False),
        show_linkedin=settings.get("show_linkedin", True),
        show_location=settings.get("show_location", True),
        discoverable_in_search=settings.get("discoverable_in_search", True),
    )


@router.patch("/profiles/me/visibility", response_model=VisibilitySettings)
async def update_visibility(
    data: VisibilityUpdate,
    profile: MarketplaceProfile = Depends(get_my_marketplace_profile),
    db: AsyncSession = Depends(get_db),
):
    update_data = data.model_dump(exclude_unset=True)

    if "is_public" in update_data:
        profile.is_public = update_data.pop("is_public")

    if update_data:
        settings = dict(profile.visibility_settings or {})
        settings.update(update_data)
        profile.visibility_settings = settings

    await db.commit()

    settings = profile.visibility_settings or {}
    return VisibilitySettings(
        is_public=profile.is_public,
        show_email=settings.get("show_email", False),
        show_phone=settings.get("show_phone", False),
        show_linkedin=settings.get("show_linkedin", True),
        show_location=settings.get("show_location", True),
        discoverable_in_search=settings.get("discoverable_in_search", True),
    )


# ── Discovery / Search ────────────────────────────────────────────


@router.get("/discover")
async def discover_profiles(
    q: str | None = None,
    profile_type: str | None = None,
    skills: str | None = None,
    location: str | None = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Browse and search public marketplace profiles."""
    stmt = (
        select(MarketplaceProfile)
        .where(MarketplaceProfile.is_public == True)
        .options(
            selectinload(MarketplaceProfile.professional_data),
            selectinload(MarketplaceProfile.advisor_data),
            selectinload(MarketplaceProfile.founder_data),
        )
    )
    count_stmt = (
        select(sa_func.count())
        .select_from(MarketplaceProfile)
        .where(MarketplaceProfile.is_public == True)
    )

    if profile_type:
        stmt = stmt.where(MarketplaceProfile.profile_type == profile_type)
        count_stmt = count_stmt.where(MarketplaceProfile.profile_type == profile_type)

    if location:
        loc_filter = MarketplaceProfile.location.ilike(f"%{location}%")
        stmt = stmt.where(loc_filter)
        count_stmt = count_stmt.where(loc_filter)

    if skills:
        skill_list = [s.strip() for s in skills.split(",") if s.strip()]
        for skill in skill_list:
            skill_filter = MarketplaceProfile.skills.op("@>")(f'["{skill}"]')
            stmt = stmt.where(skill_filter)
            count_stmt = count_stmt.where(skill_filter)

    if q:
        search_filter = or_(
            MarketplaceProfile.headline.ilike(f"%{q}%"),
            MarketplaceProfile.bio.ilike(f"%{q}%"),
            MarketplaceProfile.skills_text.ilike(f"%{q}%"),
        )
        stmt = stmt.where(search_filter)
        count_stmt = count_stmt.where(search_filter)

    stmt = stmt.order_by(MarketplaceProfile.profile_score.desc())

    offset = (page - 1) * page_size
    stmt = stmt.limit(page_size).offset(offset)

    result = await db.execute(stmt)
    profiles = result.scalars().all()
    total = (await db.execute(count_stmt)).scalar() or 0

    return {
        "items": [_build_public_view(p) for p in profiles],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }
