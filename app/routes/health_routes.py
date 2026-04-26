"""Health check routes"""

from fastapi import APIRouter
from app.models import HealthResponse
from app.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        environment=settings.ENVIRONMENT
    )


@router.get("/ready", response_model=dict)
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "ready": True,
        "timestamp": "now()"
    }
