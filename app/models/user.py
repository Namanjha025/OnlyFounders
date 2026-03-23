from typing import Optional

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import MarketplaceRole, UserRole


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        ENUM(UserRole, name="userrole", create_type=True, values_callable=lambda e: [x.value for x in e]),
        default=UserRole.FOUNDER,
        server_default=UserRole.FOUNDER.value,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    marketplace_role: Mapped[Optional[MarketplaceRole]] = mapped_column(
        ENUM(MarketplaceRole, name="marketplacerole", create_type=True,
             values_callable=lambda e: [x.value for x in e]),
        nullable=True,
    )

    founder_profile = relationship("FounderProfile", back_populates="user", uselist=False)
    startups = relationship("Startup", back_populates="creator")
    marketplace_profile = relationship("MarketplaceProfile", back_populates="user", uselist=False)
