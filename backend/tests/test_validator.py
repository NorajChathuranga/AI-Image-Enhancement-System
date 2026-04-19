from __future__ import annotations

import io

import pytest
from PIL import Image

from app.pipeline.validator import UploadValidationError, validate_upload_payload


def make_png_payload(width: int, height: int) -> bytes:
    """Create an in-memory PNG image payload."""
    image = Image.new("RGB", (width, height), color=(10, 20, 30))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_validate_upload_happy_path() -> None:
    """Valid PNG payload should pass validation."""
    payload = make_png_payload(64, 64)
    mime_type, size_bytes = validate_upload_payload(
        payload=payload,
        filename="sample.png",
        max_upload_mb=10,
        allowed_mime_types=["image/png", "image/jpeg", "image/webp"],
    )
    assert mime_type == "image/png"
    assert size_bytes > 0


def test_validate_upload_large_file_edge_case() -> None:
    """Payloads above max size should fail validation."""
    payload = b"x" * (2 * 1024 * 1024)
    with pytest.raises(UploadValidationError):
        validate_upload_payload(
            payload=payload,
            filename="too-large.png",
            max_upload_mb=1,
            allowed_mime_types=["image/png"],
        )


def test_validate_upload_corrupt_file_error_case() -> None:
    """Invalid image bytes should fail with a validation error."""
    with pytest.raises(UploadValidationError):
        validate_upload_payload(
            payload=b"invalid-image-data",
            filename="broken.png",
            max_upload_mb=10,
            allowed_mime_types=["image/png", "image/jpeg", "image/webp"],
        )
