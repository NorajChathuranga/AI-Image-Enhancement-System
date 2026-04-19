from __future__ import annotations

import re
from pathlib import Path

from app.core.config import Settings


_SAFE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")
_MIME_EXTENSION = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def sanitize_filename(filename: str) -> str:
    """Sanitize user-supplied filenames to remove unsafe characters."""
    basename = Path(filename).name
    cleaned = _SAFE_NAME_PATTERN.sub("_", basename).strip("._")
    return cleaned or "upload"


def input_path_for_job(settings: Settings, job_id: str, mime_type: str) -> Path:
    """Build a deterministic temp input path for a job."""
    extension = _MIME_EXTENSION.get(mime_type, ".img")
    return settings.resolved_temp_dir / f"{job_id}{extension}"


def output_path_for_job(settings: Settings, job_id: str) -> Path:
    """Build output path for enhanced image."""
    return settings.resolved_output_dir / f"{job_id}.webp"


def save_upload_bytes(settings: Settings, job_id: str, payload: bytes, mime_type: str) -> Path:
    """Persist raw upload bytes to temp storage."""
    path = input_path_for_job(settings, job_id, mime_type)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return path
