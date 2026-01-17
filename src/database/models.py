from datetime import datetime

from sqlalchemy import String, DateTime, Index, UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EventModel(Base):
    __tablename__ = "events"

    event_id: Mapped[UUID] = mapped_column(UUID, primary_key=True, index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    properties: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    __table_args__ = (
        Index("ix_events_occurred_at_event_type", "occurred_at", "event_type"),
        Index("ix_events_occurred_at_user_id", "occurred_at", "user_id"),
    )
