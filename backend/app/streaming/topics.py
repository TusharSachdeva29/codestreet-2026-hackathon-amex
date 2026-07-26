"""Topic selection helpers for simulator events."""

from app.core.config import Settings
from app.schemas.events import EventSource


def topic_for_source(source: EventSource, settings: Settings) -> str:
    """Return the configured Kafka topic for the given event source."""

    return settings.kafka_topic_map[source]
