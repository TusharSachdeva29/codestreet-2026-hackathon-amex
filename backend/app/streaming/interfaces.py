"""Interfaces shared by Kafka producer and API handlers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.schemas.events import EventIngestRequest


@dataclass(frozen=True)
class PublishResult:
    """Metadata returned after a Kafka publish succeeds."""

    topic: str
    partition: int
    offset: int


class EventPublisher(Protocol):
    """Protocol for publishing simulator events."""

    def publish_event(self, payload: EventIngestRequest) -> PublishResult:
        """Publish an event and return delivery metadata."""

    def close(self) -> None:
        """Release any publisher resources."""
