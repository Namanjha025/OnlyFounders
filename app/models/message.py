from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import MessageRole


class Message(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "messages"

    startup_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), index=True
    )
    role: Mapped[MessageRole] = mapped_column(
        ENUM(MessageRole, name="messagerole", create_type=True, values_callable=lambda e: [x.value for x in e]), nullable=False
    )
    content: Mapped[Optional[str]] = mapped_column(Text)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB)

    startup = relationship("Startup", backref="messages")
    agent = relationship("Agent")
