from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.feed_event import FeedEvent
from app.models.user import User
from app.schemas.feed_event import FeedEventCreate, FeedEventOut

router = APIRouter(prefix="/api/v1/feed", tags=["feed"])


def _event_out(e: FeedEvent) -> FeedEventOut:
    agent = e.agent
    ws = e.workspace
    return FeedEventOut(
        id=e.id,
        user_id=e.user_id,
        workspace_id=e.workspace_id,
        agent_id=e.agent_id,
        event_type=e.event_type,
        title=e.title,
        description=e.description,
        agent_name=agent.name if agent else None,
        agent_icon=agent.icon if agent else None,
        agent_color=agent.color if agent else None,
        workspace_name=ws.name if ws else None,
        created_at=e.created_at,
    )


@router.get("/", response_model=List[FeedEventOut])
async def list_feed(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    result = await db.execute(
        select(FeedEvent)
        .where(FeedEvent.user_id == current_user.id)
        .options(
            selectinload(FeedEvent.agent),
            selectinload(FeedEvent.workspace),
        )
        .order_by(FeedEvent.created_at.desc())
        .offset(offset).limit(limit)
    )
    return [_event_out(e) for e in result.scalars().all()]


@router.post("/", response_model=FeedEventOut, status_code=201)
async def create_feed_event(
    data: FeedEventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    event = FeedEvent(user_id=current_user.id, **data.model_dump())
    db.add(event)
    await db.commit()
    await db.refresh(event)
    result = await db.execute(
        select(FeedEvent)
        .where(FeedEvent.id == event.id)
        .options(
            selectinload(FeedEvent.agent),
            selectinload(FeedEvent.workspace),
        )
    )
    return _event_out(result.scalar_one())
