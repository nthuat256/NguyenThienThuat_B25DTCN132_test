
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), default="USER", nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime,default=lambda: datetime.now(timezone.utc),nullable=False,)

    clubs_owned = relationship("Club", back_populates="owner")
    memberships = relationship("ClubMember",back_populates="user",cascade="all, delete-orphan",)
    logs = relationship("ClubLog", back_populates="user")
    activities_assigned = relationship("ClubActivity",back_populates="assignee",)