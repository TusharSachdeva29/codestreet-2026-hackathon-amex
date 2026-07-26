"""Event ingestion endpoints for simulator-generated actions."""

from fastapi import APIRouter, status

from app.schemas.events import EventIngestRequest, EventIngestResponse

router = APIRouter()


@router.post(
    "",
    response_model=EventIngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive a simulator event",
)
def ingest_event(payload: EventIngestRequest) -> EventIngestResponse:
    """Validate and acknowledge a single simulator event."""

    return EventIngestResponse(
        accepted=True,
        event_id=payload.event_id,
        message="Event received successfully.",
    )
