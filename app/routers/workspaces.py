from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.agent import Agent
from app.models.notification import Notification
from app.models.user import User
from app.models.workspace import (
    Workspace,
    WorkspaceAgent,
    WorkspaceMessage,
    WorkspaceTask,
)
from app.schemas.workspace import (
    WorkspaceAgentOut,
    WorkspaceCreate,
    WorkspaceMessageCreate,
    WorkspaceMessageOut,
    WorkspaceOut,
    WorkspaceSummary,
    WorkspaceTaskCreate,
    WorkspaceTaskOut,
    WorkspaceTaskUpdate,
    WorkspaceUpdate,
)

router = APIRouter(prefix="/api/v1/workspaces", tags=["workspaces"])


# ── helpers ───────────────────────────────────────────────────────


async def _get_workspace(
    workspace_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> Workspace:
    result = await db.execute(
        select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.user_id == current_user.id,
            Workspace.is_active == True,
        )
    )
    ws = result.scalar_one_or_none()
    if ws is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return ws


def _agent_out(wa: WorkspaceAgent) -> WorkspaceAgentOut:
    agent = wa.agent
    return WorkspaceAgentOut(
        id=wa.id,
        agent_id=wa.agent_id,
        agent_name=agent.name if agent else None,
        agent_slug=agent.slug if agent else None,
        agent_description=agent.description if agent else None,
        agent_category=agent.category if agent else None,
        agent_icon=agent.icon if agent else None,
        agent_color=agent.color if agent else None,
        created_at=wa.created_at,
    )


def _message_out(msg: WorkspaceMessage) -> WorkspaceMessageOut:
    agent = msg.agent
    return WorkspaceMessageOut(
        id=msg.id,
        workspace_id=msg.workspace_id,
        agent_id=msg.agent_id,
        user_id=msg.user_id,
        role=msg.role,
        content=msg.content,
        action_buttons=msg.action_buttons,
        agent_name=agent.name if agent else None,
        agent_icon=agent.icon if agent else None,
        agent_color=agent.color if agent else None,
        created_at=msg.created_at,
    )


# ── workspace CRUD ────────────────────────────────────────────────


@router.get("/", response_model=List[WorkspaceSummary])
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Workspace)
        .where(Workspace.user_id == current_user.id, Workspace.is_active == True)
        .options(selectinload(Workspace.agents), selectinload(Workspace.tasks))
        .order_by(Workspace.created_at.desc())
    )
    workspaces = result.scalars().all()

    summaries = []
    for ws in workspaces:
        notif_count = await db.scalar(
            select(func.count(Notification.id)).where(
                Notification.workspace_id == ws.id,
                Notification.user_id == current_user.id,
                Notification.is_read == False,
            )
        )
        summaries.append(WorkspaceSummary(
            id=ws.id,
            name=ws.name,
            workspace_type=ws.workspace_type,
            icon=ws.icon,
            status_text=ws.status_text,
            progress=ws.progress,
            agent_count=len(ws.agents),
            task_done_count=sum(1 for t in ws.tasks if t.is_done),
            task_total_count=len(ws.tasks),
            notification_count=notif_count or 0,
            created_at=ws.created_at,
        ))
    return summaries


@router.post("/", response_model=WorkspaceOut, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ws = Workspace(user_id=current_user.id, **data.model_dump())
    db.add(ws)
    await db.commit()
    await db.refresh(ws)
    return WorkspaceOut(
        id=ws.id, user_id=ws.user_id, name=ws.name, workspace_type=ws.workspace_type,
        goal=ws.goal, brief=ws.brief, status_text=ws.status_text, progress=ws.progress,
        icon=ws.icon, is_active=ws.is_active, created_at=ws.created_at, updated_at=ws.updated_at,
    )


@router.get("/{workspace_id}", response_model=WorkspaceOut)
async def get_workspace(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Workspace)
        .where(Workspace.id == workspace_id, Workspace.user_id == current_user.id)
        .options(
            selectinload(Workspace.agents).selectinload(WorkspaceAgent.agent),
            selectinload(Workspace.tasks),
        )
    )
    ws = result.scalar_one_or_none()
    if ws is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    notif_count = await db.scalar(
        select(func.count(Notification.id)).where(
            Notification.workspace_id == ws.id,
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
    ) or 0

    return WorkspaceOut(
        id=ws.id, user_id=ws.user_id, name=ws.name, workspace_type=ws.workspace_type,
        goal=ws.goal, brief=ws.brief, status_text=ws.status_text, progress=ws.progress,
        icon=ws.icon, is_active=ws.is_active, created_at=ws.created_at, updated_at=ws.updated_at,
        agents=[_agent_out(wa) for wa in ws.agents],
        tasks=[WorkspaceTaskOut.model_validate(t) for t in ws.tasks],
        notification_count=notif_count,
    )


@router.put("/{workspace_id}", response_model=WorkspaceOut)
async def update_workspace(
    workspace_id: uuid.UUID,
    data: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ws = await _get_workspace(workspace_id, current_user, db)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(ws, key, value)
    await db.commit()
    await db.refresh(ws)
    return WorkspaceOut(
        id=ws.id, user_id=ws.user_id, name=ws.name, workspace_type=ws.workspace_type,
        goal=ws.goal, brief=ws.brief, status_text=ws.status_text, progress=ws.progress,
        icon=ws.icon, is_active=ws.is_active, created_at=ws.created_at, updated_at=ws.updated_at,
    )


# ── workspace agents ──────────────────────────────────────────────


@router.post("/{workspace_id}/agents/{agent_id}", response_model=WorkspaceAgentOut, status_code=status.HTTP_201_CREATED)
async def add_agent_to_workspace(
    workspace_id: uuid.UUID,
    agent_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ws = await _get_workspace(workspace_id, current_user, db)
    agent = await db.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    existing = await db.execute(
        select(WorkspaceAgent).where(
            WorkspaceAgent.workspace_id == ws.id,
            WorkspaceAgent.agent_id == agent_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Agent already in workspace")

    wa = WorkspaceAgent(workspace_id=ws.id, agent_id=agent_id)
    db.add(wa)
    await db.commit()
    await db.refresh(wa)
    wa.agent = agent
    return _agent_out(wa)


@router.delete("/{workspace_id}/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_agent_from_workspace(
    workspace_id: uuid.UUID,
    agent_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ws = await _get_workspace(workspace_id, current_user, db)
    result = await db.execute(
        select(WorkspaceAgent).where(
            WorkspaceAgent.workspace_id == ws.id,
            WorkspaceAgent.agent_id == agent_id,
        )
    )
    wa = result.scalar_one_or_none()
    if wa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not in workspace")
    await db.delete(wa)
    await db.commit()


# ── workspace messages ────────────────────────────────────────────


@router.get("/{workspace_id}/messages", response_model=List[WorkspaceMessageOut])
async def list_messages(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    ws = await _get_workspace(workspace_id, current_user, db)
    result = await db.execute(
        select(WorkspaceMessage)
        .where(WorkspaceMessage.workspace_id == ws.id)
        .options(selectinload(WorkspaceMessage.agent))
        .order_by(WorkspaceMessage.created_at.asc())
        .offset(offset).limit(limit)
    )
    return [_message_out(m) for m in result.scalars().all()]


@router.post("/{workspace_id}/messages", response_model=WorkspaceMessageOut, status_code=status.HTTP_201_CREATED)
async def send_message(
    workspace_id: uuid.UUID,
    data: WorkspaceMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message. If role is omitted, defaults to 'user'. agent_id can specify which agent authored it."""
    ws = await _get_workspace(workspace_id, current_user, db)

    role = data.role or "user"
    msg = WorkspaceMessage(
        workspace_id=ws.id,
        user_id=current_user.id if role == "user" else None,
        agent_id=data.agent_id,
        role=role,
        content=data.content,
    )
    db.add(msg)
    await db.commit()

    result = await db.execute(
        select(WorkspaceMessage)
        .where(WorkspaceMessage.id == msg.id)
        .options(selectinload(WorkspaceMessage.agent))
    )
    return _message_out(result.scalar_one())


# ── workspace tasks ───────────────────────────────────────────────


@router.get("/{workspace_id}/tasks", response_model=List[WorkspaceTaskOut])
async def list_workspace_tasks(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ws = await _get_workspace(workspace_id, current_user, db)
    result = await db.execute(
        select(WorkspaceTask)
        .where(WorkspaceTask.workspace_id == ws.id)
        .order_by(WorkspaceTask.created_at.asc())
    )
    return [WorkspaceTaskOut.model_validate(t) for t in result.scalars().all()]


@router.post("/{workspace_id}/tasks", response_model=WorkspaceTaskOut, status_code=status.HTTP_201_CREATED)
async def create_workspace_task(
    workspace_id: uuid.UUID,
    data: WorkspaceTaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ws = await _get_workspace(workspace_id, current_user, db)
    task = WorkspaceTask(workspace_id=ws.id, **data.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return WorkspaceTaskOut.model_validate(task)


@router.put("/{workspace_id}/tasks/{task_id}", response_model=WorkspaceTaskOut)
async def update_workspace_task(
    workspace_id: uuid.UUID,
    task_id: uuid.UUID,
    data: WorkspaceTaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ws = await _get_workspace(workspace_id, current_user, db)
    result = await db.execute(
        select(WorkspaceTask).where(
            WorkspaceTask.id == task_id,
            WorkspaceTask.workspace_id == ws.id,
        )
    )
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    await db.commit()
    await db.refresh(task)
    return WorkspaceTaskOut.model_validate(task)
