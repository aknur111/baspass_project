from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.auth_2F import Auth_2Factor


# from src.models.auth_2F import Auth_2Factor

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime
from src.config.database import Base
from datetime import datetime, timezone

from src.models.failed_login import FailedLogin
from src.models.passwords import Password



class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    email_confirmation_code: Mapped[str] = mapped_column(String(6), nullable=True)
    email_confirmation_sent_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    is_email_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    passwords: Mapped[list["Password"]] = relationship(back_populates="owner")
    failed_login: Mapped["FailedLogin"] = relationship(back_populates="user", uselist=False)
    # auth_2F: Mapped["Auth_2Factor"] = relationship("Auth_2Factor", back_populates="user", uselist=False)
    # auth_2f: Mapped["Auth_2Factor"] = relationship("Auth_2Factor", back_populates="user", uselist=False)
    # auth_2f: Mapped["Auth_2Factor"] = relationship("Auth_2Factor", back_populates="user", uselist=False)
    auth_2f: Mapped["Auth_2Factor"] = relationship("Auth_2Factor", back_populates="user", uselist=False, cascade="all, delete-orphan")
    # auth_2f: Mapped["Auth_2Factor"] = relationship("Auth_2Factor", back_populates="user", uselist=False)



