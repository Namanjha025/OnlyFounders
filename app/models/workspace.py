from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import WorkspaceMessageRole, WorkspaceType


class Workspace(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workspaces"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    workspace_type: Mapped[WorkspaceType] = mapped_column(
        ENUM(WorkspaceType, name="workspacetype", create_type=True,
             values_callable=lambda e: [x.value for x in e]),
        nullable=False, server_default=WorkspaceType.ONGOING.value,
    )
    goal: Mapped[Optional[str]] = mapped_column(Text)
    brief: Mapped[Optional[str]] = mapped_column(Text)
    status_text: Mapped[Optional[str]] = mapped_column(String(500))
    progress: Mapped[Optional[int]] = mapped_column(Integer)
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    user = relationship("User", backref="workspaces")
    agents = relationship("WorkspaceAgent", back_populates="workspace", cascade="all, delete-orphan")
    messages = relationship("WorkspaceMessage", back_populates="workspace", cascade="all, delete-orphan")
    tasks = relationship("WorkspaceTask", back_populates="workspace", cascade="all, delete-orphan")


class WorkspaceAgent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workspace_agents"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True
    )

    workspace = relationship("Workspace", back_populates="agents")
    agent = relationship("Agent")


class WorkspaceMessage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workspace_messages"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    role: Mapped[WorkspaceMessageRole] = mapped_column(
        ENUM(WorkspaceMessageRole, name="workspacemessagerole", create_type=True,
             values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    action_buttons: Mapped[Optional[dict]] = mapped_column(JSONB)

    workspace = relationship("Workspace", back_populates="messages")
    agent = relationship("Agent")


class WorkspaceTask(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workspace_tasks"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    assignee_name: Mapped[Optional[str]] = mapped_column(String(200))
    is_done: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    workspace = relationship("Workspace", back_populates="tasks")
    agent = relationship("Agent")
