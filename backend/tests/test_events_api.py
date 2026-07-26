"""Tests for the simulator event ingestion endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ingest_event_returns_acknowledgement() -> None:
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
        "message": "Event received successfully.",
    }
