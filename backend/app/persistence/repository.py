"""Event repository for MongoDB persistence."""

import logging
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.normalization.models import CanonicalEvent

logger = logging.getLogger("app.persistence.repository")

class EventRepository:
    """Handles MongoDB operations for normalized events."""
    
    def __init__(self, db: Database | None):
        self.db = db
        self.collection_name = "raw_events"
        
        if self.db is not None:
            # Create a unique index on event_id to prevent duplicates
            self.db[self.collection_name].create_index("event_id", unique=True)
            
    def save_event(self, event: CanonicalEvent) -> bool:
        """
        Persists a CanonicalEvent into MongoDB.
        Returns True if inserted successfully or False if duplicate/failed.
        """
        if self.db is None:
            logger.warning("Cannot save event: Database connection is unavailable.")
            return False
            
        try:
            document = event.model_dump(mode="json")
            # We explicitly use event_id as the unique identifier
            document["_id"] = document["event_id"]
            
            self.db[self.collection_name].insert_one(document)
            logger.info(f"Event persisted: {event.event_id}")
            return True
            
        except DuplicateKeyError:
            logger.warning(f"Duplicate event ignored: {event.event_id}")
            return False
            
        except PyMongoError as e:
            logger.error(f"Persistence failure for event {event.event_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected persistence failure for event {event.event_id}: {e}")
            return False
