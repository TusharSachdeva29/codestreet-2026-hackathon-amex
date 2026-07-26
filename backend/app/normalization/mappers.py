"""Channel-specific mapping logic for event normalization."""

import abc
from datetime import datetime
from typing import Any

from app.normalization.models import CanonicalEvent, NormalizedIdentity


class BaseEventMapper(abc.ABC):
    """Abstract base class for channel-specific event mappers."""

    @abc.abstractmethod
    def map_to_canonical(self, raw_event: dict[str, Any]) -> CanonicalEvent:
        """Map a raw channel event to the canonical event format."""
        pass

    def _extract_base_identity(self, raw_identity: dict[str, Any] | None) -> NormalizedIdentity:
        """Extract identity fields common to most events."""
        if not raw_identity:
            return NormalizedIdentity()
            
        return NormalizedIdentity(
            customer_id=raw_identity.get("customer_id"),
            email=raw_identity.get("email"),
            phone_number=raw_identity.get("phone_number"),
            device_id=raw_identity.get("device_id"),
            session_id=raw_identity.get("session_id"),
            card_last4=raw_identity.get("card_last4"),
            cookie_id=raw_identity.get("cookie_id"),
            ip_address=raw_identity.get("ip_address"),
            browser_fingerprint=raw_identity.get("browser_fingerprint"),
        )


class WebsiteEventMapper(BaseEventMapper):
    def map_to_canonical(self, raw_event: dict[str, Any]) -> CanonicalEvent:
        raw_identity = raw_event.get("identity", {})
        
        return CanonicalEvent(
            event_id=raw_event["event_id"],
            timestamp=raw_event["timestamp"],
            source="website",
            event_type=raw_event.get("event_type", "unknown_web_event"),
            identity=self._extract_base_identity(raw_identity),
            metadata=raw_event.get("metadata", {}),
            raw_event=raw_event,
        )


class MobileEventMapper(BaseEventMapper):
    def map_to_canonical(self, raw_event: dict[str, Any]) -> CanonicalEvent:
        raw_identity = raw_event.get("identity", {})
        
        return CanonicalEvent(
            event_id=raw_event["event_id"],
            timestamp=raw_event["timestamp"],
            source="mobile_app",
            event_type=raw_event.get("event_type", "unknown_mobile_event"),
            identity=self._extract_base_identity(raw_identity),
            metadata=raw_event.get("metadata", {}),
            raw_event=raw_event,
        )


class CallCentreEventMapper(BaseEventMapper):
    def map_to_canonical(self, raw_event: dict[str, Any]) -> CanonicalEvent:
        raw_identity = raw_event.get("identity", {})
        
        return CanonicalEvent(
            event_id=raw_event["event_id"],
            timestamp=raw_event["timestamp"],
            source="call_centre",
            event_type=raw_event.get("event_type", "unknown_call_event"),
            identity=self._extract_base_identity(raw_identity),
            metadata=raw_event.get("metadata", {}),
            raw_event=raw_event,
        )


class StoreEventMapper(BaseEventMapper):
    def map_to_canonical(self, raw_event: dict[str, Any]) -> CanonicalEvent:
        raw_identity = raw_event.get("identity", {})
        
        return CanonicalEvent(
            event_id=raw_event["event_id"],
            timestamp=raw_event["timestamp"],
            source="physical_store",
            event_type=raw_event.get("event_type", "unknown_store_event"),
            identity=self._extract_base_identity(raw_identity),
            metadata=raw_event.get("metadata", {}),
            raw_event=raw_event,
        )


class EventMapperFactory:
    """Factory to retrieve the appropriate mapper for an event source."""

    _mappers = {
        "website": WebsiteEventMapper(),
        "mobile_app": MobileEventMapper(),
        "call_centre": CallCentreEventMapper(),
        "physical_store": StoreEventMapper(),
    }

    @classmethod
    def get_mapper(cls, source: str) -> BaseEventMapper:
        mapper = cls._mappers.get(source)
        if not mapper:
            raise ValueError(f"No mapper registered for source: {source}")
        return mapper
