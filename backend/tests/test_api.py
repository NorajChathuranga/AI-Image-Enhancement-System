from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.routes import resolve_enhancement_options


def test_health_happy_path(client: TestClient) -> None:
    """Health endpoint should report service availability."""
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "models_loaded" in payload


def test_enhance_corrupted_file_edge_case(client: TestClient) -> None:
    """Corrupted uploads should be rejected with HTTP 400."""
    response = client.post(
        "/v1/enhance",
        files={"file": ("broken.png", b"not-a-real-image", "image/png")},
    )
    assert response.status_code == 400


def test_status_error_case_not_found(client: TestClient) -> None:
    """Unknown jobs should return HTTP 404."""
    response = client.get("/v1/status/does-not-exist")
    assert response.status_code == 404


def test_enhance_submit_happy_path(client: TestClient, png_payload: bytes) -> None:
    """Valid image upload should enqueue a job and return its ID."""
    response = client.post(
        "/v1/enhance",
        files={"file": ("sample.png", png_payload, "image/png")},
    )
    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "pending"
    assert payload["job_id"]


def test_enhance_submit_custom_controls_happy_path(client: TestClient, png_payload: bytes) -> None:
    """Valid upload with custom controls should still enqueue a job."""
    response = client.post(
        "/v1/enhance",
        files={"file": ("sample.png", png_payload, "image/png")},
        data={
            "preset": "quality",
            "scale_factor": "4",
            "denoise": "true",
            "deblur": "true",
            "face_enhance": "true",
            "output_quality": "95",
        },
    )
    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "pending"
    assert payload["job_id"]


def test_enhance_submit_rejects_invalid_preset(client: TestClient, png_payload: bytes) -> None:
    """Invalid preset should return HTTP 400 with a clear message."""
    response = client.post(
        "/v1/enhance",
        files={"file": ("sample.png", png_payload, "image/png")},
        data={"preset": "cinematic"},
    )
    assert response.status_code == 400
    assert "Invalid preset" in response.json()["detail"]


def test_resolve_enhancement_options_applies_overrides() -> None:
    """Resolver should combine preset defaults with explicit overrides."""
    options = resolve_enhancement_options(
        preset="fast",
        scale_factor=4,
        denoise=True,
        deblur=False,
        face_enhance=True,
        output_quality=92,
    )

    assert options.preset == "fast"
    assert options.scale_factor == 4
    assert options.denoise is True
    assert options.deblur is False
    assert options.face_enhance is True
    assert options.output_quality == 92


def test_resolve_enhancement_options_rejects_invalid_quality() -> None:
    """Resolver should reject output quality outside accepted range."""
    with pytest.raises(HTTPException) as exc:
        resolve_enhancement_options(
            preset="balanced",
            scale_factor=None,
            denoise=None,
            deblur=None,
            face_enhance=None,
            output_quality=101,
        )

    assert exc.value.status_code == 400
