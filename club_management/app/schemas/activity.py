from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ActivityStatus = Literal["TODO", "IN_PROGRESS", "DONE"]
ActivityPriority = Literal["LOW", "MEDIUM", "HIGH"]


class ActivityBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    assignee_id: int | None = None
    status: ActivityStatus = "TODO"
    priority: ActivityPriority = "MEDIUM"
    due_date: datetime | None = None


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    assignee_id: int | None = None
    status: ActivityStatus | None = None
    priority: ActivityPriority | None = None
    due_date: datetime | None = None


class ActivityResponse(ActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    club_id: int
    created_at: datetime