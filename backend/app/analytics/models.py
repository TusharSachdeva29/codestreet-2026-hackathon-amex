"""Models for the Journey Analytics phase."""

from typing import Any
from pydantic import BaseModel, Field

class JourneyMetrics(BaseModel):
    total_events: int = 0
    journey_duration_minutes: float = 0.0
    channels_used: list[str] = Field(default_factory=list)
    support_calls: int = 0
    payment_failures: int = 0
    kyc_failures: int = 0

class JourneyAnalytics(BaseModel):
    """Business insights derived from a customer journey."""
    
    journey_status: str = "Active"
    customer_health_score: int = 100
    metrics: JourneyMetrics = Field(default_factory=JourneyMetrics)
    friction_indicators: list[str] = Field(default_factory=list)
    business_rule_outcomes: list[str] = Field(default_factory=list)
    root_cause: str | None = None
    summary: str = "Journey initialized."
