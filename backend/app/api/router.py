"""API router registration."""

from fastapi import APIRouter

from app.api.routes.events import router as events_router
from app.api.routes.journeys import router as journeys_router
from app.api.routes.system import router as system_router
from app.api.routes.feed import router as feed_router
from app.api.routes.graph import router as graph_router

api_router = APIRouter()
api_router.include_router(events_router, prefix="/events", tags=["events"])
api_router.include_router(journeys_router, prefix="/journeys", tags=["journeys"])
api_router.include_router(system_router, prefix="/system", tags=["system"])
api_router.include_router(feed_router, prefix="/feed", tags=["feed"])
api_router.include_router(graph_router, prefix="/graph", tags=["graph"])
