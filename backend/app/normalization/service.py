"""Event normalization service to transform raw events into canonical events."""

import logging
from typing import Any

from pydantic import ValidationError

from app.normalization.mappers import EventMapperFactory
from app.normalization.models import CanonicalEvent

logger = logging.getLogger("app.normalization.service")


class EventNormalizationService:
    """Service to normalize raw events into the canonical format."""

    def normalize(self, raw_event: dict[str, Any]) -> CanonicalEvent | None:
        """
        Normalize a raw event dictionary.
        Returns the CanonicalEvent if successful, or None if validation/mapping fails.
        """
        try:
            # 1. Detect source
            source = raw_event.get("source")
            if not source:
                logger.error(f"Event missing source: {raw_event.get('event_id', 'unknown')}")
                return None

            # 2. Get mapper
            try:
                mapper = EventMapperFactory.get_mapper(source)
            except ValueError as e:
                logger.error(f"Unsupported event source: {source}")
                return None

            # 3. Map to canonical model (also performs Pydantic validation)
            canonical_event = mapper.map_to_canonical(raw_event)
            return canonical_event

        except ValidationError as e:
            logger.error(
                f"Validation failed for canonical event. Source: {raw_event.get('source')}, "
                f"Event ID: {raw_event.get('event_id', 'unknown')}. Error: {e}"
            )
            return None
        except Exception as e:
            logger.exception(
                f"Unexpected error during normalization of event ID: "
                f"{raw_event.get('event_id', 'unknown')}"
            )
            return None
