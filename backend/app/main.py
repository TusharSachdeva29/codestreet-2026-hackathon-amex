"""FastAPI application entrypoint for the Kafka-backed simulator phases."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.streaming.producer import KafkaEventProducer

settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Manage long-lived application services."""

    application.state.event_producer = KafkaEventProducer(settings=settings)
    try:
        yield
    finally:
        application.state.event_producer.close()


app = FastAPI(
    title="AMEX Journey Stitching Platform API",
    version="0.1.0",
    description="Phase 2 backend for receiving simulated customer events and publishing them to Kafka.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Provide a lightweight health response for local development."""

    return {"status": "ok"}
