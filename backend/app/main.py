"""FastAPI application entrypoint for the event simulator phase."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="AMEX Journey Stitching Platform API",
    version="0.1.0",
    description="Phase 1 backend for receiving simulated customer interaction events.",
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
