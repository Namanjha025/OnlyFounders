from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.agent import Agent
from app.models.notification import Notification
from app.models.user import User
from app.models.workspace import Workspace
from app.models.enums import NotificationType
from app.schemas.notification import NotificationCreate, NotificationOut

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


def _notif_out(n: Notification) -> NotificationOut:
    agent = n.agent
    ws = n.workspace
    return NotificationOut(
        id=n.id,
        user_id=n.user_id,
        workspace_id=n.workspace_id,
        agent_id=n.agent_id,
        notification_type=n.notification_type,
        priority=n.priority,
        title=n.title,
        description=n.description,
        detail=n.detail,
        is_read=n.is_read,
        action_buttons=n.action_buttons,
        agent_name=agent.name if agent else None,
        agent_icon=agent.icon if agent else None,
        agent_color=agent.color if agent else None,
        workspace_name=ws.name if ws else None,
        created_at=n.created_at,
    )


@router.get("/", response_model=List[NotificationOut])
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    notification_type: Optional[NotificationType] = Query(None, alias="type"),
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = (
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .options(
            selectinload(Notification.agent),
            selectinload(Notification.workspace),
        )
    )
    if notification_type is not None:
        query = query.where(Notification.notification_type == notification_type)
    if unread_only:
        query = query.where(Notification.is_read == False)
    query = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    return [_notif_out(n) for n in result.scalars().all()]


@router.get("/count")
async def unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = await db.scalar(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
    )
    return {"unread_count": count or 0}


@router.put("/{notification_id}/read", response_model=NotificationOut)
async def mark_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification)
        .where(Notification.id == notification_id, Notification.user_id == current_user.id)
        .options(
            selectinload(Notification.agent),
            selectinload(Notification.workspace),
        )
    )
    notif = result.scalar_one_or_none()
    if notif is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    notif.is_read = True
    await db.commit()
    await db.refresh(notif)
    return _notif_out(notif)


@router.put("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
    )
    for notif in result.scalars().all():
        notif.is_read = True
    await db.commit()


@router.post("/", response_model=NotificationOut, status_code=status.HTTP_201_CREATED)
async def create_notification(
    data: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    notif = Notification(user_id=current_user.id, **data.model_dump())
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    result = await db.execute(
        select(Notification)
        .where(Notification.id == notif.id)
        .options(
            selectinload(Notification.agent),
            selectinload(Notification.workspace),
        )
    )
    return _notif_out(result.scalar_one())
