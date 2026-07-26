"""Database connection management."""

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure
import logging

from app.core.config import get_settings

logger = logging.getLogger("app.core.db")

class MongoDBClient:
    """Manages the MongoDB connection."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.db = None
        
    def connect(self) -> Database:
        """Connects to MongoDB and returns the database instance."""
        if self.db is not None:
            return self.db
            
        try:
            self.client = MongoClient(
                self.settings.mongodb_uri,
                serverSelectionTimeoutMS=5000,
                uuidRepresentation='standard'
            )
            # Ping the server to verify connection
            self.client.admin.command('ping')
            self.db = self.client[self.settings.mongodb_db_name]
            logger.info("MongoDB connection established successfully.")
            return self.db
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.client = None
            self.db = None
            return None
            
    def close(self):
        """Closes the MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("MongoDB connection closed.")
