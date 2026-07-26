"""Models for the Journey Stitching phase."""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class JourneyEvent(BaseModel):
    """An event as stored within a customer journey."""
    
    event_id: UUID
    timestamp: datetime
    source: str
    event_type: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    confidence_score: float

    # For chronological ordering and deduplication
    def __hash__(self) -> int:
        return hash(self.event_id)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, JourneyEvent):
            return False
        return self.event_id == other.event_id


class CustomerJourney(BaseModel):
    """The unified timeline of all events for a specific customer."""

    customer_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    events: list[JourneyEvent] = Field(default_factory=list)
    analytics: dict[str, Any] | None = Field(default=None, description="Persisted analytics insights")
