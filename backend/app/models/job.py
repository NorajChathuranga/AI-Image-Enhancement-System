from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class Job(SQLModel, table=True):
    """Persistent enhancement job record."""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True, index=True)
    status: str = Field(default="pending", index=True)
    progress_pct: int = Field(default=0)

    input_filename: str
    input_size_bytes: int
    mime_type: str

    output_path: str | None = None
    processing_time_ms: int | None = None
    stage_times_json: str | None = None
    error_message: str | None = None
    current_stage: str | None = None

    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    completed_at: datetime | None = None
