from sqlalchemy import Column, Integer, DateTime, ForeignKey
from datetime import datetime

from sqlalchemy.orm import relationship

from src.config.database import Base

class FailedLogin(Base):
    __tablename__ = "block_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    attempts = Column(Integer, default=0)
    last_attempt = Column(DateTime, default=datetime.utcnow)
    blocked_until = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="failed_login")
