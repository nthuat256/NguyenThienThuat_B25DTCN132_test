from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class ClubActivity(Base):
    __tablename__ = "club_activities"
    __table_args__ = (
        Index("ix_activity_club_created", "club_id", "created_at"),
        Index("ix_activity_club_status", "club_id", "status"),
        Index("ix_activity_club_priority", "club_id", "priority"),
        Index("ix_activity_assignee", "assignee_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(30), default="TODO", nullable=False)
    priority = Column(String(30), default="MEDIUM", nullable=False)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    club = relationship("Club", back_populates="activities")
    assignee = relationship("User", back_populates="activities_assigned")