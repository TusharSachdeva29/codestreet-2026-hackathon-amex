# Backend

FastAPI backend for Phase 2 event streaming.

## Current Responsibility

- Receive simulator-generated events
- Validate payload shape
- Publish events to source-specific Kafka topics
- Provide a standalone Kafka consumer that logs received events

## Kafka Topics

- `web-events`
- `mobile-events`
- `callcentre-events`
- `store-events`

## Consumer Run

```powershell
.\.venv\Scripts\python.exe -m app.consumers.event_consumer
```

## Topic Bootstrap

```powershell
.\.venv\Scripts\python.exe -m app.streaming.bootstrap_topics
```

## Intentionally Excluded

- Persistence
- Analytics
- Identity resolution
- Business workflows
