"""Kafka producer used by the event ingestion API."""

from __future__ import annotations

import json
from typing import Any

from kafka import KafkaProducer

from app.core.config import Settings
from app.schemas.events import EventIngestRequest
from app.streaming.interfaces import PublishResult
from app.streaming.topics import topic_for_source


class KafkaEventProducer:
    """Publish simulator events to their channel-specific Kafka topics."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._producer: KafkaProducer | None = None

    def _get_producer(self) -> KafkaProducer:
        """Create the underlying Kafka producer on first use."""

        if self._producer is None:
            self._producer = KafkaProducer(
                bootstrap_servers=self._settings.kafka_bootstrap_servers,
                client_id=self._settings.kafka_client_id,
                key_serializer=lambda value: value.encode("utf-8"),
                value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            )
        return self._producer

    def publish_event(self, payload: EventIngestRequest) -> PublishResult:
        """Publish a single simulator event to Kafka."""

        topic = topic_for_source(payload.source, self._settings)
        event_payload: dict[str, Any] = payload.model_dump(mode="json")
        producer = self._get_producer()
        future = producer.send(
            topic=topic,
            key=str(payload.event_id),
            value=event_payload,
        )
        record_metadata = future.get(timeout=self._settings.kafka_producer_timeout_seconds)
        return PublishResult(
            topic=record_metadata.topic,
            partition=record_metadata.partition,
            offset=record_metadata.offset,
        )

    def close(self) -> None:
        """Flush and close the Kafka producer."""

        if self._producer is not None:
            self._producer.flush()
            self._producer.close()
