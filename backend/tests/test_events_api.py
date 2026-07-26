"""Tests for the simulator event ingestion endpoint."""

from app.dependencies import get_event_publisher
from fastapi.testclient import TestClient

from app.main import app
from app.streaming.interfaces import PublishResult

client = TestClient(app)


class StubPublisher:
    def publish_event(self, payload):
        return PublishResult(topic="web-events", partition=0, offset=12)

    def close(self) -> None:
        return None


def test_ingest_event_returns_acknowledgement() -> None:
    app.dependency_overrides[get_event_publisher] = lambda: StubPublisher()
    payload = {
        "event_id": "4d92d897-f95d-4ef7-b49c-76d28b80f250",
        "timestamp": "2026-07-26T10:15:00Z",
        "source": "website",
        "event_type": "open_website",
        "identity": {
            "customer_id": "cust-1001",
            "email": "customer@example.com",
            "session_id": "sess-9001",
        },
        "metadata": {
            "page": "homepage",
        },
    }

    response = client.post("/api/v1/events", json=payload)

    assert response.status_code == 202
    assert response.json() == {
        "accepted": True,
        "event_id": payload["event_id"],
        "topic": "web-events",
        "partition": 0,
        "offset": 12,
        "message": "Event received and published successfully.",
    }
    app.dependency_overrides.clear()
