from __future__ import annotations

from fastapi.testclient import TestClient


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
