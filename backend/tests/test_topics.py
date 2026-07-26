"""Tests for Kafka topic routing."""

from app.core.config import Settings
from app.streaming.topics import topic_for_source


def test_topic_for_source_matches_configured_channel_topics() -> None:
    settings = Settings()

    assert topic_for_source("website", settings) == "web-events"
    assert topic_for_source("mobile_app", settings) == "mobile-events"
    assert topic_for_source("call_centre", settings) == "callcentre-events"
    assert topic_for_source("physical_store", settings) == "store-events"
