"""Application settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the backend application."""

    api_prefix: str = "/api/v1"
    log_level: str = "INFO"
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_client_id: str = "journey-simulator-api"
    kafka_consumer_group_id: str = "journey-simulator-consumer"
    kafka_web_topic: str = "web-events"
    kafka_mobile_topic: str = "mobile-events"
    kafka_call_centre_topic: str = "callcentre-events"
    kafka_store_topic: str = "store-events"
    kafka_producer_timeout_seconds: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def kafka_topic_map(self) -> dict[str, str]:
        """Return the configured topic name for each event source."""

        return {
            "website": self.kafka_web_topic,
            "mobile_app": self.kafka_mobile_topic,
            "call_centre": self.kafka_call_centre_topic,
            "physical_store": self.kafka_store_topic,
        }

    @property
    def kafka_consumer_topics(self) -> tuple[str, ...]:
        """Return all Kafka topics consumed by the logging consumer."""

        return tuple(self.kafka_topic_map.values())


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()
