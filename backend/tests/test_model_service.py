from __future__ import annotations

from pathlib import Path

from app.core.config import Settings
from app.services.model_service import DEFAULT_CHECKPOINT_URLS, ModelService


def test_resolve_checkpoint_url_prefers_override() -> None:
    """Configured URL should override built-in URL mapping."""
    settings = Settings(skip_model_loading=True)
    service = ModelService(settings)

    resolved = service._resolve_checkpoint_url(
        checkpoint_name="GFPGANv1.3.pth",
        configured_url="https://example.com/custom-gfpgan.pth",
    )

    assert resolved == "https://example.com/custom-gfpgan.pth"


def test_resolve_checkpoint_url_uses_defaults() -> None:
    """Missing override should fall back to default URL mapping."""
    settings = Settings(skip_model_loading=True)
    service = ModelService(settings)

    resolved = service._resolve_checkpoint_url(
        checkpoint_name="GFPGANv1.3.pth",
        configured_url=None,
    )

    assert resolved == DEFAULT_CHECKPOINT_URLS["GFPGANv1.3.pth"]


def test_ensure_checkpoint_returns_existing_file(tmp_path: Path) -> None:
    """Existing checkpoint should be returned without any download attempt."""
    settings = Settings(weights_dir=tmp_path, skip_model_loading=True)
    service = ModelService(settings)

    checkpoint_path = tmp_path / "GFPGANv1.3.pth"
    checkpoint_path.write_bytes(b"existing")

    resolved_path, error = service._ensure_checkpoint(
        model_label="GFPGAN",
        checkpoint_name="GFPGANv1.3.pth",
        configured_url=None,
    )

    assert error is None
    assert resolved_path == checkpoint_path


def test_ensure_checkpoint_reports_missing_when_auto_download_disabled(tmp_path: Path) -> None:
    """Missing checkpoint should return clear message if auto-download is disabled."""
    settings = Settings(
        weights_dir=tmp_path,
        model_auto_download=False,
        skip_model_loading=True,
    )
    service = ModelService(settings)

    resolved_path, error = service._ensure_checkpoint(
        model_label="GFPGAN",
        checkpoint_name="GFPGANv1.3.pth",
        configured_url=None,
    )

    assert resolved_path is None
    assert error is not None
    assert "Enable MODEL_AUTO_DOWNLOAD=true" in error


def test_ensure_checkpoint_downloads_when_missing(tmp_path: Path, monkeypatch) -> None:
    """Missing checkpoint should be downloaded when auto-download is enabled."""
    settings = Settings(
        weights_dir=tmp_path,
        model_auto_download=True,
        skip_model_loading=True,
    )
    service = ModelService(settings)

    def fake_download(_: str, destination: Path) -> str | None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"downloaded")
        return None

    monkeypatch.setattr(service, "_download_checkpoint", fake_download)

    resolved_path, error = service._ensure_checkpoint(
        model_label="GFPGAN",
        checkpoint_name="GFPGANv1.3.pth",
        configured_url="https://example.com/GFPGANv1.3.pth",
    )

    assert error is None
    assert resolved_path is not None
    assert resolved_path.exists()
    assert resolved_path.read_bytes() == b"downloaded"
