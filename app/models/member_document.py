from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import MemberDocCategory


class MemberDocument(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "member_documents"

    startup_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    member_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startup_members.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[MemberDocCategory] = mapped_column(
        ENUM(MemberDocCategory, name="memberdoccategory", create_type=True, values_callable=lambda e: [x.value for x in e]), nullable=False
    )
    file_name: Mapped[Optional[str]] = mapped_column(String(255))
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))
    s3_key: Mapped[Optional[str]] = mapped_column(String(500))

    member = relationship("StartupMember", back_populates="documents")
