"""API router registration."""

from fastapi import APIRouter

from app.api.routes.events import router as events_router
from app.api.routes.journeys import router as journeys_router

api_router = APIRouter()
api_router.include_router(events_router, prefix="/events", tags=["events"])
api_router.include_router(journeys_router, prefix="/journeys", tags=["journeys"])
