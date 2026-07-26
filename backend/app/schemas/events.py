"""Schemas used by the event simulator ingestion API."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

EventSource = Literal["website", "mobile_app", "call_centre", "physical_store"]


class IdentityPayload(BaseModel):
    """Known customer identifiers attached to a simulator event."""

    customer_id: str | None = Field(default=None, max_length=64)
    email: EmailStr | None = None
    phone_number: str | None = Field(default=None, max_length=32)
    card_last4: str | None = Field(default=None, min_length=4, max_length=4)
    device_id: str | None = Field(default=None, max_length=128)
    session_id: str | None = Field(default=None, max_length=128)


class EventIngestRequest(BaseModel):
    """Common simulator event payload."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID
    timestamp: datetime
    source: EventSource
    event_type: str = Field(min_length=1, max_length=100)
    identity: IdentityPayload
    metadata: dict[str, Any] = Field(default_factory=dict)


class EventIngestResponse(BaseModel):
    """Acknowledgement returned after event receipt."""

    accepted: bool
    event_id: UUID
    message: str
