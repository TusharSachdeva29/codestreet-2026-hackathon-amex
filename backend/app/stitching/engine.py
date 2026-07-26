"""Journey Stitching Engine to maintain chronological customer event timelines."""

from datetime import datetime, timezone
import logging

from app.identity.models import ResolvedCustomerEvent
from app.stitching.models import CustomerJourney, JourneyEvent
from app.stitching.repository import JourneyRepository
from app.analytics.engine import JourneyAnalyticsEngine

logger = logging.getLogger("app.stitching.engine")


class JourneyStitchingEngine:
    """Stitches individual resolved events into a continuous customer journey."""

    def __init__(self, repository: JourneyRepository):
        self.repository = repository
        self.analytics_engine = JourneyAnalyticsEngine()

    def stitch(self, resolved_event: ResolvedCustomerEvent) -> CustomerJourney:
        """
        Appends the resolved event to the customer's journey, maintaining
        chronological order and eliminating duplicates.
        """
        customer_id = resolved_event.resolved_customer_id
        canonical = resolved_event.canonical_event
        
        # 1. Map to Journey Event
        journey_event = JourneyEvent(
            event_id=canonical.event_id,
            timestamp=canonical.timestamp,
            source=canonical.source,
            event_type=canonical.event_type,
            metadata=canonical.metadata,
            confidence_score=resolved_event.confidence_score
        )

        # 2. Retrieve existing journey or create a new one
        journey = self.repository.get_journey(customer_id)
        if not journey:
            journey = CustomerJourney(customer_id=customer_id)

        # 3. Deduplication Check
        existing_event_ids = {e.event_id for e in journey.events}
        if journey_event.event_id in existing_event_ids:
            logger.info(f"Duplicate event {journey_event.event_id} detected for customer {customer_id}. Skipping.")
            return journey

        # 4. Append and Sort
        journey.events.append(journey_event)
        # Ensure chronological ordering by timestamp
        journey.events.sort(key=lambda e: e.timestamp)

        # 5. Calculate Analytics
        analytics = self.analytics_engine.analyze(journey)
        journey.analytics = analytics.model_dump(mode="json")

        # 6. Update Metadata
        journey.updated_at = datetime.now(timezone.utc)

        # 7. Persist
        self.repository.save_journey(journey)
        
        return journey
