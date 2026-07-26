"""System status and overview endpoints."""

from fastapi import APIRouter
from app.stitching.repository import FileBasedJourneyRepository
from app.core.db import MongoDBClient

router = APIRouter()
journey_repo = FileBasedJourneyRepository()
mongo_client = MongoDBClient()

@router.get("/status", summary="Get system status")
def get_system_status():
    db = mongo_client.connect()
    db_status = "Online" if db is not None else "Offline"
    
    return {
        "status": "Healthy",
        "kafka": "Online", # Mocked for simplicity in this phase
        "database": db_status,
        "uptime": "99.9%"
    }

@router.get("/overview", summary="Get dashboard overview metrics")
def get_overview():
    # Simple analytics from file-based repo
    journeys = []
    if journey_repo.data_dir.exists():
        for file_path in journey_repo.data_dir.glob("*.json"):
            customer_id = file_path.stem
            journey = journey_repo.get_journey(customer_id)
            if journey:
                journeys.append(journey)
                
    total_customers = len(journeys)
    active_customers = len([j for j in journeys if j.analytics and j.analytics.get('journey_status') == 'Active'])
    completed_journeys = len([j for j in journeys if j.analytics and j.analytics.get('journey_status') == 'Completed'])
    abandoned_journeys = len([j for j in journeys if j.analytics and j.analytics.get('journey_status') == 'Abandoned'])
    
    total_events = sum(len(j.events) for j in journeys)
    
    avg_health = 100
    if total_customers > 0:
        health_scores = [j.analytics.get('customer_health_score', 100) for j in journeys if j.analytics]
        if health_scores:
            avg_health = sum(health_scores) / len(health_scores)
            
    return {
        "total_customers": total_customers,
        "active_customers": active_customers,
        "total_journeys": total_customers,
        "events_processed": total_events,
        "avg_health_score": round(avg_health),
        "completed_journeys": completed_journeys,
        "abandoned_journeys": abandoned_journeys
    }
