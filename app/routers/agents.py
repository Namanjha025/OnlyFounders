from __future__ import annotations

import re
import uuid
from typing import List

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.startup import require_startup_access, require_startup_owner
from app.models.agent import Agent
from app.models.enums import MemberRole
from app.models.startup import Startup
from app.models.startup_member import StartupMember
from app.models.message import Message
from app.models.enums import MessageRole
from app.models.user import User
from app.schemas.agent import AgentCreate, AgentOut, AgentRegister, AgentUpdate
from app.schemas.message import MessageCreate, MessageOut
from app.schemas.startup_member import StartupMemberOut

# --- Agent Registry (browse available agents) ---

registry_router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "agent"


@registry_router.get("/", response_model=List[AgentOut])
async def list_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Agent).where(Agent.is_active == True).order_by(Agent.name)
    )
    return [AgentOut.model_validate(a) for a in result.scalars().all()]


@registry_router.get("/{agent_id}", response_model=AgentOut)
async def get_agent(agent_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return AgentOut.model_validate(agent)


@registry_router.post("/", response_model=AgentOut, status_code=status.HTTP_201_CREATED)
async def create_agent(
    data: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Agent).where(Agent.slug == data.slug))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")
    agent = Agent(**data.model_dump())
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return AgentOut.model_validate(agent)


@registry_router.post("/register", response_model=AgentOut, status_code=status.HTTP_201_CREATED)
async def register_agent(
    data: AgentRegister,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register an external agent via its A2A Agent Card URL.

    Fetches ``{agent_url}/.well-known/agent.json``, extracts profile
    information, and creates the agent in the platform registry.
    """
    card_url = data.agent_url.rstrip("/") + "/.well-known/agent.json"

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(card_url)
            resp.raise_for_status()
            card = resp.json()
        except httpx.HTTPStatusError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Agent card not found at {card_url} (HTTP {resp.status_code})",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to fetch agent card from {card_url}: {exc}",
            )

    name = card.get("name")
    if not name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Agent card missing required 'name' field",
        )

    slug = _slugify(name)
    base_slug = slug

    result = await db.execute(select(Agent).where(Agent.slug == slug))
    counter = 1
    while result.scalar_one_or_none():
        slug = f"{base_slug}-{counter}"
        result = await db.execute(select(Agent).where(Agent.slug == slug))
        counter += 1

    metadata = card.get("metadata", {})
    skill_names = [s.get("name", s.get("id", "")) for s in card.get("skills", [])]

    agent = Agent(
        name=name,
        slug=slug,
        description=card.get("description"),
        agent_type="platform",
        endpoint_url=data.agent_url.rstrip("/"),
        agent_card=card,
        category=metadata.get("category"),
        icon=metadata.get("icon"),
        color=metadata.get("color"),
        skills=skill_names or None,
        capabilities=card.get("capabilities"),
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return AgentOut.model_validate(agent)


@registry_router.put("/{agent_id}", response_model=AgentOut)
async def update_agent(
    agent_id: uuid.UUID,
    data: AgentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(agent, key, value)
    await db.commit()
    await db.refresh(agent)
    return AgentOut.model_validate(agent)


# --- Startup Agent Team (add/remove agents from a startup) ---

team_router = APIRouter(prefix="/api/v1/startups/{startup_id}/agents", tags=["startup-agents"])


@team_router.get("/", response_model=List[StartupMemberOut])
async def list_startup_agents(
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StartupMember).where(
            StartupMember.startup_id == startup.id,
            StartupMember.agent_id != None,
        )
    )
    return [StartupMemberOut.model_validate(m) for m in result.scalars().all()]


@team_router.post("/", response_model=StartupMemberOut, status_code=status.HTTP_201_CREATED)
async def add_agent_to_team(
    agent_id: uuid.UUID,
    startup: Startup = Depends(require_startup_owner),
    db: AsyncSession = Depends(get_db),
):
    # Check agent exists
    result = await db.execute(select(Agent).where(Agent.id == agent_id, Agent.is_active == True))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    # Check not already on team
    result = await db.execute(
        select(StartupMember).where(
            StartupMember.startup_id == startup.id,
            StartupMember.agent_id == agent_id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agent already on team")

    member = StartupMember(
        startup_id=startup.id,
        agent_id=agent_id,
        name=agent.name,
        role=MemberRole.EMPLOYEE,
        title=agent.name,
        responsibilities=agent.description,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return StartupMemberOut.model_validate(member)


@team_router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_agent_from_team(
    agent_id: uuid.UUID,
    startup: Startup = Depends(require_startup_owner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StartupMember).where(
            StartupMember.startup_id == startup.id,
            StartupMember.agent_id == agent_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not on team")
    await db.delete(member)
    await db.commit()


# --- Agent Chat (invoke / messages) ---

chat_router = APIRouter(prefix="/api/v1/startups/{startup_id}/agents/{agent_id}/chat", tags=["agent-chat"])


@chat_router.get("/messages", response_model=List[MessageOut])
async def get_messages(
    agent_id: uuid.UUID,
    startup: Startup = Depends(require_startup_access),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Message)
        .where(Message.startup_id == startup.id, Message.agent_id == agent_id)
        .order_by(Message.created_at.asc())
    )
    return [MessageOut.model_validate(m) for m in result.scalars().all()]


@chat_router.post("/invoke", response_model=MessageOut)
async def invoke_agent(
    agent_id: uuid.UUID,
    data: MessageCreate,
    startup: Startup = Depends(require_startup_access),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StartupMember).where(
            StartupMember.startup_id == startup.id,
            StartupMember.agent_id == agent_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent not on this team")

    agent_result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = agent_result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    user_msg = Message(
        startup_id=startup.id,
        agent_id=agent_id,
        role=MessageRole.USER,
        content=data.content,
    )
    db.add(user_msg)
    await db.flush()

    reply_text = "[Agent response placeholder — integration pending]"

    if agent.endpoint_url:
        history_result = await db.execute(
            select(Message)
            .where(Message.startup_id == startup.id, Message.agent_id == agent_id)
            .order_by(Message.created_at.asc())
            .limit(50)
        )
        history = []
        for m in history_result.scalars().all():
            role_str = m.role.value if hasattr(m.role, "value") else str(m.role)
            history.append({
                "role": "assistant" if role_str in ("assistant", "ai") else "user",
                "content": m.content,
            })

        chat_url = agent.endpoint_url.rstrip("/") + "/chat"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(chat_url, json={
                    "message": data.content,
                    "history": history,
                })
                resp.raise_for_status()
                reply_text = resp.json().get("message", reply_text)
        except Exception as e:
            reply_text = f"[Agent communication error: {e}]"

    assistant_msg = Message(
        startup_id=startup.id,
        agent_id=agent_id,
        role=MessageRole.ASSISTANT,
        content=reply_text,
    )
    db.add(assistant_msg)

    await db.commit()
    await db.refresh(assistant_msg)
    return MessageOut.model_validate(assistant_msg)
