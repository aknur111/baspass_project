from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.users import User

# from src.models.users import User

from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.config.database import Base


class Auth_2Factor(Base):
    __tablename__ = "auth_2f"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    confirmation_2F_code: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    expired_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    failed_attempts: Mapped[int] = mapped_column(default=0)

    # user = relationship("User", back_populates="auth_2f")
    user: Mapped["User"] = relationship("User", back_populates="auth_2f")

