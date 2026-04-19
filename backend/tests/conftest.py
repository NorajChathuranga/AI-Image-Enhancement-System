from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def client(tmp_path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Create isolated FastAPI test client with temporary storage and DB."""
    db_path = tmp_path / "test_jobs.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("TEMP_DIR", str((tmp_path / "temp").as_posix()))
    monkeypatch.setenv("OUTPUT_DIR", str((tmp_path / "output").as_posix()))
    monkeypatch.setenv("WEIGHTS_DIR", str((tmp_path / "weights").as_posix()))
    monkeypatch.setenv("SKIP_MODEL_LOADING", "true")
    monkeypatch.setenv("RATE_LIMIT", "100/minute")

    from app.core.config import get_settings

    get_settings.cache_clear()

    from app.main import create_application

    app = create_application()
    with TestClient(app) as test_client:
        yield test_client

    get_settings.cache_clear()


@pytest.fixture
def png_payload() -> bytes:
    """Generate a small valid PNG payload for upload tests."""
    image = Image.new("RGB", (32, 32), color=(120, 80, 220))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
