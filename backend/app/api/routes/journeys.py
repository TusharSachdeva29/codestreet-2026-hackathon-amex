"""Journey retrieval endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.stitching.models import CustomerJourney
from app.stitching.repository import FileBasedJourneyRepository

router = APIRouter()
repo = FileBasedJourneyRepository()


@router.get(
    "/{customer_id}",
    response_model=CustomerJourney,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a customer's unified journey",
)
def get_customer_journey(customer_id: str) -> CustomerJourney:
    """Fetch the chronologically ordered event timeline for a specific customer."""
    
    journey = repo.get_journey(customer_id)
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer journey not found for ID: {customer_id}",
        )
    return journey


@router.get(
    "/{customer_id}/analytics",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a customer's journey analytics",
)
def get_customer_analytics(customer_id: str) -> dict:
    """Fetch just the analytics insights for a specific customer."""
    
    journey = repo.get_journey(customer_id)
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer journey not found for ID: {customer_id}",
        )
        
    if not journey.analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No analytics have been generated for customer ID: {customer_id} yet.",
        )
        
    return journey.analytics
