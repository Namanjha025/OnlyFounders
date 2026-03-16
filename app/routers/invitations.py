from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.startup import require_startup_owner
from app.models.enums import InvitationStatus
from app.models.invitation import Invitation
from app.models.startup import Startup
from app.models.startup_member import StartupMember
from app.models.user import User
from app.schemas.invitation import InvitationCreate, InvitationOut

# Startup-scoped routes (send invite, list invites for a startup)
startup_router = APIRouter(
    prefix="/api/v1/startups/{startup_id}/invitations",
    tags=["invitations"],
)

# User-scoped routes (my invitations, accept, decline)
user_router = APIRouter(
    prefix="/api/v1",
    tags=["invitations"],
)


@startup_router.post("/", response_model=InvitationOut, status_code=status.HTTP_201_CREATED)
async def send_invitation(
    data: InvitationCreate,
    startup: Startup = Depends(require_startup_owner),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send an invitation to a platform user to join the startup team."""
    # Can't invite yourself
    if data.invited_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot invite yourself",
        )

    # Check invited user exists
    result = await db.execute(select(User).where(User.id == data.invited_user_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invited user not found",
        )

    # Check user isn't already a member
    result = await db.execute(
        select(StartupMember).where(
            StartupMember.startup_id == startup.id,
            StartupMember.user_id == data.invited_user_id,
        )
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a team member",
        )

    # Check no pending invite already exists
    result = await db.execute(
        select(Invitation).where(
            Invitation.startup_id == startup.id,
            Invitation.invited_user_id == data.invited_user_id,
            Invitation.status == InvitationStatus.PENDING,
        )
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pending invitation already exists for this user",
        )

    invitation = Invitation(
        startup_id=startup.id,
        invited_by=current_user.id,
        **data.model_dump(),
    )
    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)
    return InvitationOut.model_validate(invitation)


@startup_router.get("/", response_model=List[InvitationOut])
async def list_startup_invitations(
    startup: Startup = Depends(require_startup_owner),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all invitations sent for this startup."""
    result = await db.execute(
        select(Invitation).where(Invitation.startup_id == startup.id)
    )
    return [InvitationOut.model_validate(i) for i in result.scalars().all()]


@user_router.get("/me/invitations", response_model=List[InvitationOut])
async def list_my_invitations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all pending invitations for the current user."""
    result = await db.execute(
        select(Invitation).where(
            Invitation.invited_user_id == current_user.id,
            Invitation.status == InvitationStatus.PENDING,
        )
    )
    return [InvitationOut.model_validate(i) for i in result.scalars().all()]


@user_router.put("/invitations/{invitation_id}/accept", response_model=InvitationOut)
async def accept_invitation(
    invitation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Accept an invitation and join the startup team."""
    invitation = await _get_actionable_invitation(invitation_id, current_user, db)

    # Mark accepted
    invitation.status = InvitationStatus.ACCEPTED
    invitation.responded_at = datetime.now(timezone.utc)

    # Create startup member from invitation details
    member = StartupMember(
        startup_id=invitation.startup_id,
        user_id=current_user.id,
        name=f"{current_user.first_name} {current_user.last_name}",
        email=current_user.email,
        role=invitation.role,
        title=invitation.title,
        responsibilities=invitation.responsibilities,
    )
    db.add(member)
    await db.commit()
    await db.refresh(invitation)
    return InvitationOut.model_validate(invitation)


@user_router.put("/invitations/{invitation_id}/decline", response_model=InvitationOut)
async def decline_invitation(
    invitation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Decline an invitation."""
    invitation = await _get_actionable_invitation(invitation_id, current_user, db)

    invitation.status = InvitationStatus.DECLINED
    invitation.responded_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(invitation)
    return InvitationOut.model_validate(invitation)


async def _get_actionable_invitation(
    invitation_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> Invitation:
    """Fetch a pending invitation that belongs to the current user."""
    result = await db.execute(
        select(Invitation).where(Invitation.id == invitation_id)
    )
    invitation = result.scalar_one_or_none()
    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )
    if invitation.invited_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation is not for you",
        )
    if invitation.status != InvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invitation already {invitation.status.value}",
        )
    # Check expiry
    if invitation.expires_at and invitation.expires_at < datetime.now(timezone.utc):
        invitation.status = InvitationStatus.EXPIRED
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )
    return invitation
