"""Standalone Kafka consumer for simulator event logging."""

from __future__ import annotations

import json
import logging

from kafka import KafkaConsumer

from app.core.config import get_settings
from app.normalization.service import EventNormalizationService
from app.identity.graph import IdentityGraph
from app.identity.engine import IdentityResolutionEngine

logger = logging.getLogger("app.consumers.event_consumer")


def build_consumer() -> KafkaConsumer:
    """Create a Kafka consumer subscribed to all simulator topics."""

    settings = get_settings()
    return KafkaConsumer(
        *settings.kafka_consumer_topics,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        client_id=f"{settings.kafka_client_id}-consumer",
        group_id=settings.kafka_consumer_group_id,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        key_deserializer=lambda value: value.decode("utf-8") if value else None,
    )


def run() -> None:
    """Run the logging consumer loop."""

    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(message)s",
    )

    consumer = build_consumer()
    logger.info(
        json.dumps(
            {
                "event": "consumer_started",
                "topics": list(settings.kafka_consumer_topics),
                "bootstrap_servers": settings.kafka_bootstrap_servers,
            }
        )
    )

    normalizer = EventNormalizationService()
    
    # Initialize the identity graph (in-memory for this phase)
    identity_graph = IdentityGraph()
    identity_engine = IdentityResolutionEngine(identity_graph)

    try:
        for message in consumer:
            raw_payload = message.value
            canonical = normalizer.normalize(raw_payload)
            
            if canonical:
                # Resolve the identity of the event
                resolved_event = identity_engine.resolve(canonical)

                logger.info(
                    json.dumps(
                        {
                            "event": "identity_resolved",
                            "topic": message.topic,
                            "partition": message.partition,
                            "offset": message.offset,
                            "key": message.key,
                            "canonical_event_id": str(canonical.event_id),
                            "resolved_customer_id": resolved_event.resolved_customer_id,
                            "confidence": resolved_event.confidence_score,
                            "resolved_event_payload": json.loads(resolved_event.model_dump_json()),
                        }
                    )
                )
            else:
                logger.warning(
                    json.dumps(
                        {
                            "event": "event_normalization_failed",
                            "topic": message.topic,
                            "partition": message.partition,
                            "offset": message.offset,
                            "key": message.key,
                            "payload": raw_payload,
                        }
                    )
                )
    except KeyboardInterrupt:
        logger.info(json.dumps({"event": "consumer_stopped"}))
    finally:
        consumer.close()


if __name__ == "__main__":
    run()
