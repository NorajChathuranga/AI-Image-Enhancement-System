from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.core.config import Settings
from app.pipeline.orchestrator import run_pipeline
from app.services.job_service import JobService
from app.services.model_service import ModelService
from app.services.storage_service import output_path_for_job


logger = logging.getLogger(__name__)


def _coerce_bool(value: object, default: bool) -> bool:
    """Coerce a dynamic value to boolean with a fallback default."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def _coerce_int(value: object, default: int) -> int:
    """Coerce a dynamic value to int with a fallback default."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def process_enhancement_job(
    job_id: str,
    input_path: str,
    settings: Settings,
    model_service: ModelService,
    enhancement_options: dict[str, Any] | None = None,
) -> None:
    """Run enhancement pipeline for a single job in a background task."""
    jobs = JobService()
    jobs.mark_processing(job_id)

    try:
        output_path = output_path_for_job(settings, job_id)
        options = enhancement_options or {}
        scale_factor = _coerce_int(options.get("scale_factor"), settings.scale_factor)
        denoise_enabled = _coerce_bool(options.get("denoise"), True)
        deblur_enabled = _coerce_bool(options.get("deblur"), True)
        face_enhance_enabled = _coerce_bool(options.get("face_enhance"), True)
        output_quality = _coerce_int(options.get("output_quality"), 88)

        def on_progress(percent: int, stage: str) -> None:
            jobs.update_progress(job_id, percent, stage)

        result = run_pipeline(
            input_path=Path(input_path),
            output_path=output_path,
            runtime=model_service.runtime,
            scale_factor=scale_factor,
            denoise_enabled=denoise_enabled,
            deblur_enabled=deblur_enabled,
            face_enhance_enabled=face_enhance_enabled,
            output_quality=output_quality,
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
