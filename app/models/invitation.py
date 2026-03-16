from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import InvitationStatus, MemberRole


class Invitation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "invitations"

    startup_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    invited_by: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    invited_user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[MemberRole] = mapped_column(
        ENUM(MemberRole, name="memberrole", create_type=False, values_callable=lambda e: [x.value for x in e]), nullable=False
    )
    title: Mapped[Optional[str]] = mapped_column(String(100))
    responsibilities: Mapped[Optional[str]] = mapped_column(Text)
    message: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[InvitationStatus] = mapped_column(
        ENUM(
            InvitationStatus,
            name="invitationstatus",
            create_type=True,
            values_callable=lambda e: [x.value for x in e],
        ),
        nullable=False,
        default=InvitationStatus.PENDING,
    )
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    responded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

    startup = relationship("Startup")
    inviter = relationship("User", foreign_keys=[invited_by])
    invitee = relationship("User", foreign_keys=[invited_user_id])
