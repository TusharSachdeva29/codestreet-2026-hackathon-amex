"""Event ingestion endpoints for simulator-generated actions."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from kafka.errors import KafkaError

from app.dependencies import get_event_publisher
from app.schemas.events import EventIngestRequest, EventIngestResponse
from app.streaming.interfaces import EventPublisher

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=EventIngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive a simulator event",
)
def ingest_event(
    payload: EventIngestRequest,
    publisher: EventPublisher = Depends(get_event_publisher),
) -> EventIngestResponse:
    """Validate an event and publish it to the matching Kafka topic."""

    try:
        result = publisher.publish_event(payload)
    except KafkaError as exc:
        logger.exception("Failed to publish simulator event to Kafka.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to publish event to Kafka.",
        ) from exc

    return EventIngestResponse(
        accepted=True,
        event_id=payload.event_id,
        topic=result.topic,
        partition=result.partition,
        offset=result.offset,
        message="Event received and published successfully.",
    )
