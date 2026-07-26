"""Models for the Identity Resolution phase."""

from typing import Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from app.normalization.models import CanonicalEvent


class IdentityNode(BaseModel):
    """A node in the identity graph representing a single identifier."""
    
    id_type: str  # e.g., "email", "device_id", "cookie_id", "phone_number"
    id_value: str

    def __hash__(self) -> int:
        return hash((self.id_type, self.id_value))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, IdentityNode):
            return False
        return self.id_type == other.id_type and self.id_value == other.id_value


class GraphNode(BaseModel):
    """Persistent Node in MongoDB."""
    id: str  # e.g., 'email:jdoe@example.com'
    id_type: str
    id_value: str
    customer_id: str
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GraphEdge(BaseModel):
    """Persistent Edge in MongoDB representing relationships."""
    source: str
    target: str
    relationship_type: str = "CONNECTED_TO"
    confidence: float
    evidence: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResolvedCustomerEvent(BaseModel):
    """An event enriched with resolved customer identity information."""

    canonical_event: CanonicalEvent
    resolved_customer_id: str
    confidence_score: float = Field(default=1.0, description="1.0 for deterministic matches")
    linked_identifiers: dict[str, str] = Field(default_factory=dict, description="Other identifiers known for this customer")
    explanation: list[str] = Field(default_factory=list, description="Reasoning for the merge decision")
