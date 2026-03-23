from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class TeamAgent(Base, UUIDMixin, TimestampMixin):
    """An agent hired onto a user's startup team with a custom role and JD."""

    __tablename__ = "team_agents"
    __table_args__ = (
        UniqueConstraint("user_id", "agent_id", name="uq_team_user_agent"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[Optional[str]] = mapped_column(String(200))
    job_description: Mapped[Optional[str]] = mapped_column(Text)

    user = relationship("User", backref="team_agents")
    agent = relationship("Agent")
