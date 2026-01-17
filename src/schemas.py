from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EventIn(BaseModel):
    event_id: UUID
    occurred_at: datetime
    user_id: str = Field(min_length=1, max_length=128)
    event_type: str = Field(min_length=1, max_length=64)
    properties: dict[str, str] = Field(default_factory=dict)

