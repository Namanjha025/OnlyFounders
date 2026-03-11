from __future__ import annotations

import datetime
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.startup import require_startup_access
from app.models.calendar_event import CalendarEvent
from app.models.enums import CalendarEventType
from app.models.startup import Startup
from app.models.user import User
from app.schemas.calendar_event import CalendarEventCreate, CalendarEventOut, CalendarEventUpdate

router = APIRouter(prefix="/api/v1/startups/{startup_id}/calendar", tags=["calendar"])


@router.get("/", response_model=List[CalendarEventOut])
async def list_events(
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
    event_type: Optional[CalendarEventType] = Query(None, alias="type"),
    from_date: Optional[datetime.date] = Query(None),
    to_date: Optional[datetime.date] = Query(None),
):
    query = select(CalendarEvent).where(CalendarEvent.startup_id == startup.id)
    if event_type is not None:
        query = query.where(CalendarEvent.event_type == event_type)
    if from_date is not None:
        query = query.where(CalendarEvent.event_date >= from_date)
    if to_date is not None:
        query = query.where(CalendarEvent.event_date <= to_date)
    query = query.order_by(CalendarEvent.event_date.asc())

    result = await db.execute(query)
    return [CalendarEventOut.model_validate(e) for e in result.scalars().all()]


@router.post("/", response_model=CalendarEventOut, status_code=status.HTTP_201_CREATED)
async def create_event(
    data: CalendarEventCreate,
    startup: Startup = Depends(require_startup_access),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    event = CalendarEvent(
        startup_id=startup.id,
        created_by_user=current_user.id,
        **data.model_dump(),
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return CalendarEventOut.model_validate(event)


@router.put("/{event_id}", response_model=CalendarEventOut)
async def update_event(
    event_id: uuid.UUID,
    data: CalendarEventUpdate,
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CalendarEvent).where(
            CalendarEvent.id == event_id, CalendarEvent.startup_id == startup.id
        )
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(event, key, value)

    await db.commit()
    await db.refresh(event)
    return CalendarEventOut.model_validate(event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: uuid.UUID,
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CalendarEvent).where(
            CalendarEvent.id == event_id, CalendarEvent.startup_id == startup.id
        )
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    await db.delete(event)
    await db.commit()
