import pytest
import uuid
from datetime import datetime, timezone, timedelta

from app.stitching.engine import JourneyStitchingEngine
from app.stitching.repository import JourneyRepository
from app.stitching.models import CustomerJourney
from app.identity.models import ResolvedCustomerEvent
from app.normalization.models import CanonicalEvent, NormalizedIdentity

class InMemoryMockRepo(JourneyRepository):
    def __init__(self):
        self.db = {}
        
    def get_journey(self, customer_id: str):
        return self.db.get(customer_id)
        
    def save_journey(self, journey: CustomerJourney):
        self.db[journey.customer_id] = journey


def test_stitching_engine():
    repo = InMemoryMockRepo()
    engine = JourneyStitchingEngine(repo)
    
    customer_id = "CUST-123"
    event_1_id = uuid.uuid4()
    
    canonical_1 = CanonicalEvent(
        event_id=event_1_id,
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=5),
        source="website",
        event_type="login",
        identity=NormalizedIdentity(email="test@example.com"),
        raw_event={}
    )
    
    resolved_1 = ResolvedCustomerEvent(
        canonical_event=canonical_1,
        resolved_customer_id=customer_id,
        confidence_score=1.0,
        linked_identifiers={"email": "test@example.com"}
    )
    
    # 1. Stitch first event
    journey = engine.stitch(resolved_1)
    
    assert len(journey.events) == 1
    assert journey.events[0].event_id == event_1_id
    
    # 2. Test Deduplication
    journey = engine.stitch(resolved_1)
    assert len(journey.events) == 1  # Should still be 1
    
    # 3. Test chronological ordering
    event_2_id = uuid.uuid4()
    canonical_2 = CanonicalEvent(
        event_id=event_2_id,
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=10), # Older than event 1!
        source="mobile_app",
        event_type="install",
        identity=NormalizedIdentity(device_id="dev_1"),
        raw_event={}
    )
    
    resolved_2 = ResolvedCustomerEvent(
        canonical_event=canonical_2,
        resolved_customer_id=customer_id,
        confidence_score=1.0,
        linked_identifiers={"device_id": "dev_1"}
    )
    
    journey = engine.stitch(resolved_2)
    assert len(journey.events) == 2
    
    # event_2 is older, so it should be the first item in the sorted journey
    assert journey.events[0].event_id == event_2_id
    assert journey.events[1].event_id == event_1_id
