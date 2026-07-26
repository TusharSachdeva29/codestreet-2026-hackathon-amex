import pytest
import uuid
from datetime import datetime, timezone, timedelta

from app.stitching.models import CustomerJourney, JourneyEvent
from app.analytics.engine import JourneyAnalyticsEngine


def create_mock_event(event_type: str, minutes_ago: int, source: str = "website") -> JourneyEvent:
    return JourneyEvent(
        event_id=uuid.uuid4(),
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=minutes_ago),
        source=source,
        event_type=event_type,
        confidence_score=1.0
    )


def test_analytics_metrics_and_friction():
    engine = JourneyAnalyticsEngine()
    
    # 1. Empty journey
    empty_journey = CustomerJourney(customer_id="CUST-EMPTY")
    analytics = engine.analyze(empty_journey)
    assert analytics.metrics.total_events == 0
    assert analytics.journey_status == "Active"

    # 2. Journey with KYC and Payment failures
    events = [
        create_mock_event("login", 60),
        create_mock_event("kyc_failed", 55),
        create_mock_event("kyc_failed", 50),
        create_mock_event("payment_failed", 45),
        create_mock_event("payment_failed", 40),
        create_mock_event("payment_failed", 35), # 3 payment failures
        create_mock_event("support_call", 30, "call_centre"),
        create_mock_event("support_call", 25, "call_centre"), # 2 support calls
    ]
    
    journey = CustomerJourney(customer_id="CUST-1", events=events)
    analytics = engine.analyze(journey)
    
    # Check metrics
    assert analytics.metrics.total_events == 8
    assert analytics.metrics.kyc_failures == 2
    assert analytics.metrics.payment_failures == 3
    assert analytics.metrics.support_calls == 2
    assert "website" in analytics.metrics.channels_used
    assert "call_centre" in analytics.metrics.channels_used
    
    # Check friction & root cause
    assert "High Payment Risk" in analytics.friction_indicators
    assert "Customer Frustration" in analytics.friction_indicators
    assert "Verification Issue" in analytics.friction_indicators
    assert analytics.root_cause in ["Verification Issue", "High Payment Risk", "Customer Frustration"]
    
    # Health score should be penalized heavily
    assert analytics.customer_health_score < 50
    assert analytics.journey_status == "Active" # Did not complete or abandon yet


def test_completed_healthy_journey():
    engine = JourneyAnalyticsEngine()
    
    events = [
        create_mock_event("started_application", 10),
        create_mock_event("application_submitted", 5) # completed
    ]
    
    journey = CustomerJourney(customer_id="CUST-2", events=events)
    analytics = engine.analyze(journey)
    
    assert analytics.journey_status == "Completed"
    assert analytics.customer_health_score > 90
    assert len(analytics.friction_indicators) == 0
    assert analytics.root_cause is None
    assert "successfully" not in analytics.summary.lower() or "completed" in analytics.summary.lower()


def test_inactive_journey():
    engine = JourneyAnalyticsEngine()
    
    events = [
        # Very old event, > 30 days
        create_mock_event("login", 60 * 24 * 35)
    ]
    
    journey = CustomerJourney(customer_id="CUST-3", events=events)
    analytics = engine.analyze(journey)
    
    assert "Inactive Customer" in analytics.friction_indicators
    assert analytics.root_cause == "Inactive Customer"
    assert analytics.customer_health_score < 100
