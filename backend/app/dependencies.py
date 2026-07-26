"""Shared FastAPI dependencies."""

from fastapi import Request

from app.streaming.interfaces import EventPublisher


def get_event_publisher(request: Request) -> EventPublisher:
    """Return the Kafka-backed event publisher stored on the app state."""

    return request.app.state.event_producer
