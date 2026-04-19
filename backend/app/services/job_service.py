from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.database import engine
from app.models.job import Job


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class JobService:
    """Service for job record creation and state transitions."""

    def create_job(
        self,
        *,
        job_id: str,
        input_filename: str,
        input_size_bytes: int,
        mime_type: str,
    ) -> Job:
        """Create and persist a pending job record."""
        with Session(engine) as session:
            job = Job(
                id=job_id,
                status="pending",
                progress_pct=0,
                input_filename=input_filename,
                input_size_bytes=input_size_bytes,
                mime_type=mime_type,
            )
            session.add(job)
            session.commit()
            session.refresh(job)
            return job

    def get_job(self, job_id: str) -> Job | None:
        """Fetch a job by id."""
        with Session(engine) as session:
            return session.get(Job, job_id)

    def list_jobs(self, limit: int = 20) -> list[Job]:
        """Return recent jobs ordered by creation time."""
        normalized_limit = max(1, min(limit, 200))
        with Session(engine) as session:
            query = select(Job).order_by(Job.created_at.desc()).limit(normalized_limit)
            return list(session.exec(query))

    def queue_depth(self) -> int:
        """Return count of queued and in-progress jobs."""
        with Session(engine) as session:
            query = select(Job).where(Job.status.in_(("pending", "processing")))
            return len(list(session.exec(query)))

    def mark_processing(self, job_id: str) -> None:
        """Set job status to processing."""
        self._update_job(
            job_id,
            status="processing",
            progress_pct=5,
            current_stage="pipeline_start",
        )

    def update_progress(self, job_id: str, progress_pct: int, stage: str) -> None:
        """Update job progress and current stage."""
        self._update_job(job_id, progress_pct=max(0, min(progress_pct, 100)), current_stage=stage)

    def mark_complete(
        self,
        job_id: str,
        output_path: str,
        processing_time_ms: int,
        stage_times: dict[str, int],
    ) -> None:
        """Set job to complete with timing metadata."""
        self._update_job(
            job_id,
            status="complete",
            progress_pct=100,
            output_path=output_path,
            processing_time_ms=processing_time_ms,
            stage_times_json=json.dumps(stage_times),
            completed_at=utc_now(),
            error_message=None,
            current_stage="complete",
        )

    def mark_failed(self, job_id: str, error_message: str) -> None:
        """Set job status to failed with safe error message."""
        self._update_job(
            job_id,
            status="failed",
            progress_pct=100,
            error_message=error_message,
            completed_at=utc_now(),
            current_stage="failed",
        )

    def _update_job(self, job_id: str, **fields: object) -> None:
        """Apply field updates to a job record if found."""
        with Session(engine) as session:
            job = session.get(Job, job_id)
            if job is None:
                return
            for key, value in fields.items():
                setattr(job, key, value)
            session.add(job)
            session.commit()
