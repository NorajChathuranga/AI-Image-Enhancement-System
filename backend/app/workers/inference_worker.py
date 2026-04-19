from __future__ import annotations

import logging
from pathlib import Path

from app.core.config import Settings
from app.pipeline.orchestrator import run_pipeline
from app.services.job_service import JobService
from app.services.model_service import ModelService
from app.services.storage_service import output_path_for_job


logger = logging.getLogger(__name__)


def process_enhancement_job(
    job_id: str,
    input_path: str,
    settings: Settings,
    model_service: ModelService,
) -> None:
    """Run enhancement pipeline for a single job in a background task."""
    jobs = JobService()
    jobs.mark_processing(job_id)

    try:
        output_path = output_path_for_job(settings, job_id)

        def on_progress(percent: int, stage: str) -> None:
            jobs.update_progress(job_id, percent, stage)

        result = run_pipeline(
            input_path=Path(input_path),
            output_path=output_path,
            runtime=model_service.runtime,
            scale_factor=settings.scale_factor,
            progress_callback=on_progress,
        )

        jobs.mark_complete(
            job_id,
            output_path=str(result.output_path),
            processing_time_ms=result.total_time_ms,
            stage_times=result.stage_times_ms,
        )
    except Exception:
        logger.exception("Enhancement job failed for %s.", job_id)
        jobs.mark_failed(job_id, "Enhancement failed during processing.")
