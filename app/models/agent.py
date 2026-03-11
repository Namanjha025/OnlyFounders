from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import AgentType


class Agent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "agents"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    agent_type: Mapped[AgentType] = mapped_column(
        ENUM(AgentType, name="agenttype", create_type=True, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        server_default=AgentType.PLATFORM.value,
    )
    system_prompt: Mapped[Optional[str]] = mapped_column(Text)
    skills: Mapped[Optional[dict]] = mapped_column(JSONB)
    tools_config: Mapped[Optional[dict]] = mapped_column(JSONB)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
