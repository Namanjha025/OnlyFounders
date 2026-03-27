from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.startup import require_startup_access
from app.models.agent import Agent
from app.models.enums import MessageRole
from app.models.message import Message
from app.models.startup import Startup
from app.models.startup_member import StartupMember
from app.models.user import User
from app.schemas.message import MessageCreate, MessageOut

MANAGER_SLUG = "manager"

router = APIRouter(prefix="/api/v1/startups/{startup_id}/chat", tags=["manager-chat"])


async def _get_manager_agent(db: AsyncSession) -> Agent:
    """Fetch the Manager agent from the registry."""
    result = await db.execute(
        select(Agent).where(Agent.slug == MANAGER_SLUG, Agent.is_active == True)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Manager agent not configured",
        )
    return agent


async def _require_manager_on_team(
    startup: Startup, agent: Agent, db: AsyncSession
) -> StartupMember:
    """Verify Manager agent is on this startup's team."""
    result = await db.execute(
        select(StartupMember).where(
            StartupMember.startup_id == startup.id,
            StartupMember.agent_id == agent.id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager agent not assigned to this startup",
        )
    return member


@router.get("/messages", response_model=List[MessageOut])
async def get_manager_messages(
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_manager_agent(db)
    await _require_manager_on_team(startup, agent, db)

    result = await db.execute(
        select(Message)
        .where(Message.startup_id == startup.id, Message.agent_id == agent.id)
        .order_by(Message.created_at.asc())
    )
    return [MessageOut.model_validate(m) for m in result.scalars().all()]


@router.post("/invoke", response_model=MessageOut)
async def invoke_manager(
    data: MessageCreate,
    startup: Startup = Depends(require_startup_access),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_manager_agent(db)
    await _require_manager_on_team(startup, agent, db)

    user_msg = Message(
        startup_id=startup.id,
        agent_id=agent.id,
        role=MessageRole.USER,
        content=data.content,
    )
    db.add(user_msg)

    assistant_msg = Message(
        startup_id=startup.id,
        agent_id=agent.id,
        role=MessageRole.ASSISTANT,
        content="[Manager response placeholder — agent integration pending]",
    )
    db.add(assistant_msg)

    await db.commit()
    await db.refresh(assistant_msg)
    return MessageOut.model_validate(assistant_msg)
