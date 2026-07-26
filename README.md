# American Express Cross-Channel Journey Stitching Platform

Repository scaffold for an event-driven, microservice-inspired platform.

## Status

Phase 2 event streaming ready.

## Scope Included

- Four channel simulators in the frontend
- Backend API for receiving simulated events
- Kafka producer integration in the backend
- Kafka consumer for structured event logging
- Shared event schema for simulator requests
- Documentation scaffolding and project context

## Scope Excluded

- Database setup
- Identity resolution
- Event stitching
- Journey analytics
- Authentication and authorization

## Repository Layout

- `backend/` FastAPI event ingestion API
- `frontend/` Next.js App Router simulator UI
- `docs/` documentation placeholders
- `sample-data/` local sample payload placeholders

## Phase 2 Flow

Simulator page
-> backend API
-> Kafka producer
-> Kafka topic
-> Kafka consumer
-> application log

## Kafka Topics

- `web-events`
- `mobile-events`
- `callcentre-events`
- `store-events`

## Local Run

### Kafka

```powershell
docker compose up -d kafka
```

### Topic Bootstrap

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.streaming.bootstrap_topics
```

### Backend

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### Consumer

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.consumers.event_consumer
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000` by default. Override this using `NEXT_PUBLIC_API_BASE_URL`.

## Next Steps

Introduce event normalization on top of the Kafka consumer flow in the next phase.
