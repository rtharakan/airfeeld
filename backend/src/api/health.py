"""
Health Check Endpoint

Provides system health status for monitoring.
Returns database connectivity and overall system status.
"""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.database import get_session

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(description="Overall health status")
    timestamp: str = Field(description="Check timestamp (ISO 8601)")
    version: str = Field(description="Application version")
    database: str = Field(description="Database connection status")


class ReadinessResponse(BaseModel):
    """Readiness check response for Kubernetes."""
    
    ready: bool = Field(description="Whether the service is ready")
    checks: dict[str, bool] = Field(description="Individual check results")


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check overall system health status.",
)
async def health_check(
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> HealthResponse:
    """
    Check system health.
    
    Verifies database connectivity and returns overall status.
    """
    # Check database
    db_status = "healthy"
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"
    
    overall_status = "healthy" if db_status == "healthy" else "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=settings.app_version,
        database=db_status,
    )


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Kubernetes liveness probe. Returns 200 if process is running.",
)
async def liveness_probe() -> dict[str, str]:
    """
    Liveness probe for Kubernetes.
    
    Simply returns OK to indicate the process is alive.
    """
    return {"status": "alive"}


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description="Kubernetes readiness probe. Checks if service can handle requests.",
)
async def readiness_probe(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReadinessResponse:
    """
    Readiness probe for Kubernetes.
    
    Verifies all dependencies are available before accepting traffic.
    """
    checks: dict[str, bool] = {}
    
    # Check database
    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        checks["database"] = False
    
    # All checks must pass for readiness
    ready = all(checks.values())
    
    return ReadinessResponse(ready=ready, checks=checks)
