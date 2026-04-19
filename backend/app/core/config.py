from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Image Enhancer API"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/v1"

    allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )
    allowed_origin_regex: str = r"https?://(localhost|127\.0\.0\.1)(:\d+)?$"
    allowed_mime_types: list[str] = Field(
        default_factory=lambda: [
            "image/jpeg",
            "image/png",
            "image/webp",
        ]
    )

    max_upload_mb: int = 10
    rate_limit: str = "10/minute"
    cleanup_hours: int = 1
    cleanup_interval_seconds: int = 1800

    poll_interval_ms: int = 2000
    database_url: str = "sqlite:///./backend/jobs.db"

    temp_dir: Path = Path("backend/temp")
    output_dir: Path = Path("backend/output")
    weights_dir: Path = Path("backend/weights")

    model_checkpoint_realesrgan: str = "realesr-general-x4v3.pth"
    model_checkpoint_gfpgan: str = "GFPGANv1.4.pth"

    scale_factor: int = 4
    tile_size: int = 512
    tile_pad: int = 10
    pre_pad: int = 0
    fp16_default: bool = True

    skip_model_loading: bool = False

    @property
    def project_root(self) -> Path:
        """Return the project root directory."""
        return Path(__file__).resolve().parents[3]

    def resolve_path(self, path_value: Path) -> Path:
        """Resolve a relative path against project root."""
        if path_value.is_absolute():
            return path_value
        return self.project_root / path_value

    @property
    def resolved_temp_dir(self) -> Path:
        """Absolute path for upload temp storage."""
        return self.resolve_path(self.temp_dir)

    @property
    def resolved_output_dir(self) -> Path:
        """Absolute path for processed image storage."""
        return self.resolve_path(self.output_dir)

    @property
    def resolved_weights_dir(self) -> Path:
        """Absolute path for model checkpoints."""
        return self.resolve_path(self.weights_dir)

    def ensure_directories(self) -> None:
        """Create required runtime directories if missing."""
        for directory in (
            self.resolved_temp_dir,
            self.resolved_output_dir,
            self.resolved_weights_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
