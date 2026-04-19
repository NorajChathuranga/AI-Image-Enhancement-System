from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Request

from app.models.schemas import HealthResponse
from app.services.job_service import JobService


router = APIRouter(tags=["health"])


@router.get("/", summary="API metadata")
async def root(request: Request) -> dict[str, str]:
    """Return API metadata."""
    settings = request.app.state.settings
    return {
        "name": settings.app_name,
        "version": settings.app_version,
    }


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health(request: Request) -> HealthResponse:
    """Return health status and model load state."""
    model_service = request.app.state.model_service
    uptime_seconds = int(
        (datetime.now(timezone.utc) - request.app.state.started_at).total_seconds()
    )
    queue_depth = JobService().queue_depth()

    return HealthResponse(
        status="ok",
        models_loaded=model_service.runtime.models_loaded,
        uptime_seconds=max(0, uptime_seconds),
        queue_depth=queue_depth,
    )
