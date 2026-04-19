from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class EnhanceResponse(BaseModel):
    """Response after enqueuing an enhancement job."""

    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    """Current job status payload."""

    job_id: str
    status: str
    progress_pct: int
    processing_time_ms: int | None
    error: str | None
    stage: str | None


class JobRecord(BaseModel):
    """Serialized job record for history endpoint."""

    job_id: str
    status: str
    input_filename: str
    input_size_bytes: int
    processing_time_ms: int | None
    created_at: datetime
    completed_at: datetime | None


class JobHistoryResponse(BaseModel):
    """List response for recent jobs."""

    jobs: list[JobRecord]


class HealthResponse(BaseModel):
    """Health probe response."""

    status: str
    models_loaded: bool
    uptime_seconds: int
    queue_depth: int
