from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.startup import require_startup_access
from app.models.enums import TaskStatus
from app.models.startup import Startup
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/api/v1/startups/{startup_id}/tasks", tags=["tasks"])


@router.get("/", response_model=List[TaskOut])
async def list_tasks(
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
    task_status: Optional[TaskStatus] = Query(None, alias="status"),
    assigned_to: Optional[uuid.UUID] = Query(None),
):
    query = select(Task).where(Task.startup_id == startup.id)
    if task_status is not None:
        query = query.where(Task.status == task_status)
    if assigned_to is not None:
        query = query.where(Task.assigned_to == assigned_to)
    query = query.order_by(Task.created_at.desc())

    result = await db.execute(query)
    return [TaskOut.model_validate(t) for t in result.scalars().all()]


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    startup: Startup = Depends(require_startup_access),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = Task(
        startup_id=startup.id,
        **data.model_dump(),
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return TaskOut.model_validate(task)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: uuid.UUID,
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.startup_id == startup.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskOut.model_validate(task)


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.startup_id == startup.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_data = data.model_dump(exclude_unset=True)

    if "status" in update_data and update_data["status"] == TaskStatus.COMPLETED:
        task.completed_at = datetime.now(timezone.utc)

    for key, value in update_data.items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return TaskOut.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.startup_id == startup.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    await db.delete(task)
    await db.commit()
