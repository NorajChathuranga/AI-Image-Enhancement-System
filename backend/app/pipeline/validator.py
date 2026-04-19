from __future__ import annotations

import io

from PIL import Image, UnidentifiedImageError


class UploadValidationError(ValueError):
    """Raised when an uploaded file fails validation checks."""


def detect_mime_type(payload: bytes) -> str:
    """Detect MIME type from file bytes using magic bytes when available."""
    try:
        import magic

        detected = magic.from_buffer(payload, mime=True)
        if isinstance(detected, str) and detected:
            return detected
    except Exception:
        pass

    try:
        with Image.open(io.BytesIO(payload)) as image:
            image_format = (image.format or "").upper()
        mapping = {
            "JPEG": "image/jpeg",
            "JPG": "image/jpeg",
            "PNG": "image/png",
            "WEBP": "image/webp",
        }
        if image_format in mapping:
            return mapping[image_format]
    except (UnidentifiedImageError, OSError):
        pass

    return "application/octet-stream"


def validate_upload_payload(
    payload: bytes,
    filename: str,
    max_upload_mb: int,
    allowed_mime_types: list[str],
) -> tuple[str, int]:
    """Validate upload payload and return MIME type and size."""
    if not payload:
        raise UploadValidationError("Uploaded file is empty.")

    size_bytes = len(payload)
    max_size_bytes = max_upload_mb * 1024 * 1024
    if size_bytes > max_size_bytes:
        raise UploadValidationError(
            f"File exceeds {max_upload_mb}MB size limit."
        )

    detected_mime = detect_mime_type(payload)
    if detected_mime not in allowed_mime_types:
        raise UploadValidationError(
            f"Unsupported file type for {filename}. Allowed: {', '.join(allowed_mime_types)}"
        )

    try:
        with Image.open(io.BytesIO(payload)) as image:
            width, height = image.size
        if width <= 0 or height <= 0:
            raise UploadValidationError("Image dimensions are invalid.")
    except (UnidentifiedImageError, OSError) as exc:
        raise UploadValidationError("Corrupted image file.") from exc

    return detected_mime, size_bytes
