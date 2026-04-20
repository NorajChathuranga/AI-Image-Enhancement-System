from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from PIL import Image

from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.models.schemas import EnhanceResponse, JobHistoryResponse, JobRecord, JobStatusResponse
from app.pipeline.validator import UploadValidationError, validate_upload_payload
from app.services.job_service import JobService
from app.services.storage_service import sanitize_filename, save_upload_bytes
from app.workers.inference_worker import process_enhancement_job


logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix=settings.api_v1_prefix, tags=["jobs"])

PRESET_PROFILES: dict[str, dict[str, int | bool]] = {
    "fast": {
        "scale_factor": 2,
        "denoise": False,
        "deblur": False,
        "face_enhance": False,
        "output_quality": 82,
    },
    "balanced": {
        "scale_factor": 4,
        "denoise": True,
        "deblur": True,
        "face_enhance": True,
        "output_quality": 88,
    },
    "custom": {
        "scale_factor": 4,
        "denoise": True,
        "deblur": True,
        "face_enhance": True,
        "output_quality": 88,
    },
    "quality": {
        "scale_factor": 4,
        "denoise": True,
        "deblur": True,
        "face_enhance": True,
        "output_quality": 94,
    },
}
ALLOWED_SCALE_FACTORS = {2, 4}
MIN_OUTPUT_QUALITY = 70
MAX_OUTPUT_QUALITY = 100


@dataclass(frozen=True)
class EnhancementOptions:
    """Validated runtime options for a single enhancement job."""

    preset: str
    scale_factor: int
    denoise: bool
    deblur: bool
    face_enhance: bool
    output_quality: int

    def as_dict(self) -> dict[str, str | int | bool]:
        """Serialize options for worker handoff."""
        return {
            "preset": self.preset,
            "scale_factor": self.scale_factor,
            "denoise": self.denoise,
            "deblur": self.deblur,
            "face_enhance": self.face_enhance,
            "output_quality": self.output_quality,
        }


def resolve_enhancement_options(
    preset: str,
    scale_factor: int | None,
    denoise: bool | None,
    deblur: bool | None,
    face_enhance: bool | None,
    output_quality: int | None,
) -> EnhancementOptions:
    """Resolve preset defaults and apply user overrides."""
    normalized_preset = (preset or "balanced").strip().lower()
    if normalized_preset not in PRESET_PROFILES:
        allowed = ", ".join(sorted(PRESET_PROFILES))
        raise HTTPException(status_code=400, detail=f"Invalid preset. Use one of: {allowed}.")

    defaults = PRESET_PROFILES[normalized_preset]
    resolved_scale = scale_factor if scale_factor is not None else int(defaults["scale_factor"])
    resolved_quality = (
        output_quality if output_quality is not None else int(defaults["output_quality"])
    )

    if resolved_scale not in ALLOWED_SCALE_FACTORS:
        raise HTTPException(status_code=400, detail="Invalid scale_factor. Use 2 or 4.")

    if resolved_quality < MIN_OUTPUT_QUALITY or resolved_quality > MAX_OUTPUT_QUALITY:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid output_quality. "
                f"Use a value between {MIN_OUTPUT_QUALITY} and {MAX_OUTPUT_QUALITY}."
            ),
        )

    return EnhancementOptions(
        preset=normalized_preset,
        scale_factor=resolved_scale,
        denoise=denoise if denoise is not None else bool(defaults["denoise"]),
        deblur=deblur if deblur is not None else bool(defaults["deblur"]),
        face_enhance=(
            face_enhance if face_enhance is not None else bool(defaults["face_enhance"])
        ),
        output_quality=resolved_quality,
    )


@router.post("/enhance", response_model=EnhanceResponse, status_code=202)
@limiter.limit(settings.rate_limit)
async def submit_enhancement(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    preset: str = Form(default="balanced"),
    scale_factor: int | None = Form(default=None),
    denoise: bool | None = Form(default=None),
    deblur: bool | None = Form(default=None),
    face_enhance: bool | None = Form(default=None),
    output_quality: int | None = Form(default=None),
) -> EnhanceResponse:
    """Accept an image upload and schedule async enhancement."""
    jobs = JobService()

    safe_name = sanitize_filename(file.filename or "upload")
    payload = await file.read()

    try:
        detected_mime, size_bytes = validate_upload_payload(
            payload=payload,
            filename=safe_name,
            max_upload_mb=settings.max_upload_mb,
            allowed_mime_types=settings.allowed_mime_types,
        )
    except UploadValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    options = resolve_enhancement_options(
        preset=preset,
        scale_factor=scale_factor,
        denoise=denoise,
        deblur=deblur,
        face_enhance=face_enhance,
        output_quality=output_quality,
    )

    try:
        job_id = str(uuid4())
        input_path = save_upload_bytes(settings, job_id, payload, detected_mime)
        jobs.create_job(
            job_id=job_id,
            input_filename=safe_name,
            input_size_bytes=size_bytes,
            mime_type=detected_mime,
        )

        background_tasks.add_task(
            process_enhancement_job,
            job_id,
            str(input_path),
            settings,
            request.app.state.model_service,
            options.as_dict(),
        )

        return EnhanceResponse(job_id=job_id, status="pending")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to accept enhancement job.")
        raise HTTPException(status_code=500, detail="Unable to submit enhancement job.")


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str) -> JobStatusResponse:
    """Return current status of a submitted job."""
    job = JobService().get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        progress_pct=job.progress_pct,
        processing_time_ms=job.processing_time_ms,
        error=job.error_message,
        stage=job.current_stage,
    )


@router.get("/result/{job_id}", response_model=None)
async def get_result(
    job_id: str,
    output_format: str = Query(default="webp", alias="format"),
) -> FileResponse | StreamingResponse:
    """Stream enhanced image output for a completed job."""
    job = JobService().get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.status != "complete" or not job.output_path:
        raise HTTPException(status_code=409, detail="Result is not ready yet.")

    output_path = Path(job.output_path)
    if not output_path.exists() or not output_path.is_file():
        raise HTTPException(status_code=404, detail="Result file not found.")

    normalized_format = output_format.lower()
    if normalized_format == "jpeg":
        normalized_format = "jpg"
    if normalized_format not in {"webp", "png", "jpg"}:
        raise HTTPException(status_code=400, detail="Invalid format. Use webp, png, or jpg.")

    if normalized_format == "webp":
        return FileResponse(
            path=output_path,
            media_type="image/webp",
            filename=f"{job_id}.webp",
        )

    media_type = "image/png" if normalized_format == "png" else "image/jpeg"
    save_format = "PNG" if normalized_format == "png" else "JPEG"
    output_buffer = io.BytesIO()

    try:
        with Image.open(output_path) as image:
            if save_format == "JPEG":
                image.convert("RGB").save(output_buffer, format="JPEG", quality=95, optimize=True)
            else:
                # Keep PNG export fast for large outputs to avoid client timeouts.
                image.save(output_buffer, format="PNG", compress_level=3)
    except Exception as exc:
        logger.exception("Failed to convert result for job %s to %s.", job_id, normalized_format)
        raise HTTPException(status_code=500, detail="Unable to convert result to requested format.") from exc

    output_buffer.seek(0)

    return StreamingResponse(
        content=output_buffer,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{job_id}.{normalized_format}"',
        },
    )


@router.get("/jobs", response_model=JobHistoryResponse)
async def list_jobs(limit: int = Query(default=20, ge=1, le=100)) -> JobHistoryResponse:
    """Return recent enhancement jobs."""
    records = [
        JobRecord(
            job_id=job.id,
            status=job.status,
            input_filename=job.input_filename,
            input_size_bytes=job.input_size_bytes,
            processing_time_ms=job.processing_time_ms,
            created_at=job.created_at,
            completed_at=job.completed_at,
        )
        for job in JobService().list_jobs(limit=limit)
    ]

    return JobHistoryResponse(jobs=records)
