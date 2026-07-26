"""Persistence layer for customer journeys."""

import abc
import json
import logging
from pathlib import Path
from typing import Optional

from app.stitching.models import CustomerJourney, JourneyEvent

logger = logging.getLogger("app.stitching.repository")


class JourneyRepository(abc.ABC):
    """Abstract interface for journey persistence."""

    @abc.abstractmethod
    def get_journey(self, customer_id: str) -> Optional[CustomerJourney]:
        pass

    @abc.abstractmethod
    def save_journey(self, journey: CustomerJourney) -> None:
        pass


class FileBasedJourneyRepository(JourneyRepository):
    """
    A simple file-based persistence layer acting as a document store (like MongoDB).
    Journeys are saved as JSON files in a dedicated directory.
    """

    def __init__(self, data_dir: str = ".data/journeys"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, customer_id: str) -> Path:
        # Sanitize customer_id just in case
        safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in customer_id)
        return self.data_dir / f"{safe_id}.json"

    def get_journey(self, customer_id: str) -> Optional[CustomerJourney]:
        file_path = self._get_file_path(customer_id)
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return CustomerJourney.model_validate(data)
        except Exception as e:
            logger.error(f"Failed to read journey for {customer_id}: {e}")
            return None

    def save_journey(self, journey: CustomerJourney) -> None:
        file_path = self._get_file_path(journey.customer_id)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                # Store as strict JSON
                json_data = journey.model_dump_json()
                f.write(json_data)
        except Exception as e:
            logger.error(f"Failed to save journey for {journey.customer_id}: {e}")
