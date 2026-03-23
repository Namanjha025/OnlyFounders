from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.agent import Agent
from app.models.team_agent import TeamAgent
from app.models.user import User
from app.schemas.team_agent import TeamAgentCreate, TeamAgentOut, TeamAgentUpdate

router = APIRouter(prefix="/api/v1/team", tags=["team"])


def _team_out(ta: TeamAgent) -> TeamAgentOut:
    agent = ta.agent
    return TeamAgentOut(
        id=ta.id,
        user_id=ta.user_id,
        agent_id=ta.agent_id,
        role=ta.role,
        job_description=ta.job_description,
        agent_name=agent.name if agent else None,
        agent_slug=agent.slug if agent else None,
        agent_description=agent.description if agent else None,
        agent_category=agent.category if agent else None,
        agent_icon=agent.icon if agent else None,
        agent_color=agent.color if agent else None,
        agent_capabilities=agent.capabilities if agent else None,
        created_at=ta.created_at,
        updated_at=ta.updated_at,
    )


@router.get("/", response_model=List[TeamAgentOut])
async def list_team(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TeamAgent)
        .where(TeamAgent.user_id == current_user.id)
        .options(selectinload(TeamAgent.agent))
        .order_by(TeamAgent.created_at.asc())
    )
    return [_team_out(ta) for ta in result.scalars().all()]


@router.post("/", response_model=TeamAgentOut, status_code=status.HTTP_201_CREATED)
async def hire_agent(
    data: TeamAgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await db.get(Agent, data.agent_id)
    if agent is None or not agent.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    existing = await db.execute(
        select(TeamAgent).where(
            TeamAgent.user_id == current_user.id,
            TeamAgent.agent_id == data.agent_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Agent already on your team")

    ta = TeamAgent(
        user_id=current_user.id,
        agent_id=data.agent_id,
        role=data.role or agent.name,
        job_description=data.job_description or agent.description,
    )
    db.add(ta)
    await db.commit()

    result = await db.execute(
        select(TeamAgent)
        .where(TeamAgent.id == ta.id)
        .options(selectinload(TeamAgent.agent))
    )
    return _team_out(result.scalar_one())


@router.put("/{team_agent_id}", response_model=TeamAgentOut)
async def update_team_agent(
    team_agent_id: uuid.UUID,
    data: TeamAgentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TeamAgent)
        .where(TeamAgent.id == team_agent_id, TeamAgent.user_id == current_user.id)
        .options(selectinload(TeamAgent.agent))
    )
    ta = result.scalar_one_or_none()
    if ta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team agent not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(ta, key, value)
    await db.commit()
    await db.refresh(ta)
    return _team_out(ta)


@router.delete("/{team_agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_team(
    team_agent_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TeamAgent).where(
            TeamAgent.id == team_agent_id,
            TeamAgent.user_id == current_user.id,
        )
    )
    ta = result.scalar_one_or_none()
    if ta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team agent not found")
    await db.delete(ta)
    await db.commit()
