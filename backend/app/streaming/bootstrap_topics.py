"""Create Kafka topics required for the simulator channels."""

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from app.core.config import get_settings


def run() -> None:
    """Create the configured simulator topics if they do not exist."""

    settings = get_settings()
    admin_client = KafkaAdminClient(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        client_id=f"{settings.kafka_client_id}-admin",
    )
    try:
        topics = [
            NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
            for topic_name in settings.kafka_consumer_topics
        ]
        try:
            admin_client.create_topics(new_topics=topics, validate_only=False)
        except TopicAlreadyExistsError:
            pass
    finally:
        admin_client.close()


if __name__ == "__main__":
    run()
