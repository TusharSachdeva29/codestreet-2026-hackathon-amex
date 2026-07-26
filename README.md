# American Express Cross-Channel Journey Stitching Platform

Repository scaffold for an event-driven, microservice-inspired platform.

## Status

Phase 1 event simulator in progress.

## Scope Included

- Four channel simulators in the frontend
- Backend API for receiving simulated events
- Shared event schema for simulator requests
- Documentation scaffolding and project context

## Scope Excluded

- Kafka integration
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

## Phase 1 Flow

Simulator page
-> backend API

## Local Run

### Backend

```powershell
cd backend
uvicorn app.main:app --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000` by default. Override this using `NEXT_PUBLIC_API_BASE_URL`.

## Next Steps

Add Kafka producer integration in the next phase without changing simulator behavior.
