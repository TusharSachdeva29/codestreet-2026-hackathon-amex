"""Live event feed endpoints."""

from fastapi import APIRouter
from app.core.db import MongoDBClient

router = APIRouter()
mongo_client = MongoDBClient()

@router.get("", summary="Get live event feed")
def get_live_events(limit: int = 50):
    db = mongo_client.connect()
    if db is None:
        return {"events": []}
        
    cursor = db["raw_events"].find().sort("timestamp", -1).limit(limit)
    events = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        events.append(doc)
        
    return {"events": events}
