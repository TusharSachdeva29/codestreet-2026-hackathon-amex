"""Canonical event model for normalized customer events."""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class NormalizedIdentity(BaseModel):
    """Standardized identity information across all channels."""

    customer_id: str | None = None
    email: str | None = None
    phone_number: str | None = None
    device_id: str | None = None
    session_id: str | None = None
    card_last4: str | None = None


class CanonicalEvent(BaseModel):
    """A standardized event format for all downstream consumers."""

    event_id: UUID
    timestamp: datetime
    source: str
    event_type: str
    identity: NormalizedIdentity
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    # Enrichment fields
    event_version: str = "1.0"
    processed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_event: dict[str, Any] = Field(description="The original unparsed raw event payload.")

