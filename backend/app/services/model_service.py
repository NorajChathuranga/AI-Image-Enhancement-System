from __future__ import annotations

import importlib
import logging
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from app.core.config import Settings


logger = logging.getLogger(__name__)


DEFAULT_CHECKPOINT_URLS: dict[str, str] = {
    "GFPGANv1.3.pth": (
        "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth"
    ),
    "realesr-general-x4v3.pth": (
        "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth"
    ),
}


def _ensure_torchvision_compat() -> None:
    """Expose compatibility alias for older torchvision import paths."""
    legacy_name = "torchvision.transforms.functional_tensor"
    try:
        importlib.import_module(legacy_name)
        return
    except ModuleNotFoundError:
        pass

    try:
        shim = importlib.import_module("torchvision.transforms._functional_tensor")
    except ModuleNotFoundError:
        return

    # Third-party packages still import the removed public module path.
    sys.modules[legacy_name] = shim


@dataclass
class ModelRuntime:
    """Container for runtime-loaded AI model instances."""

    gfpgan_model: Any | None = None
    realesrgan_model: Any | None = None
    errors: dict[str, str] = field(default_factory=dict)
    loaded_at: datetime | None = None

    @property
    def models_loaded(self) -> bool:
        """Return True when both core models are available."""
        return self.gfpgan_model is not None and self.realesrgan_model is not None


class ModelService:
    """Load and hold model instances for process lifetime reuse."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self.runtime = ModelRuntime()

    def load_models(self) -> ModelRuntime:
        """Load configured model checkpoints into memory once."""
        self.runtime = ModelRuntime()

        if self._settings.skip_model_loading:
            logger.info("Model loading is disabled by configuration.")
            return self.runtime

        gfpgan_model, gfpgan_error = self._load_gfpgan()
        if gfpgan_error:
            self.runtime.errors["gfpgan"] = gfpgan_error
        self.runtime.gfpgan_model = gfpgan_model

        realesrgan_model, realesrgan_error = self._load_realesrgan()
        if realesrgan_error:
            self.runtime.errors["realesrgan"] = realesrgan_error
        self.runtime.realesrgan_model = realesrgan_model

        self.runtime.loaded_at = datetime.now(timezone.utc)

        if self.runtime.models_loaded:
            logger.info("All AI models loaded successfully.")
        else:
            logger.warning("Model loading completed with fallbacks: %s", self.runtime.errors)

        return self.runtime

    def _resolve_checkpoint_url(self, checkpoint_name: str, configured_url: str | None) -> str | None:
        """Resolve download URL for a checkpoint using config override then defaults."""
        if configured_url and configured_url.strip():
            return configured_url.strip()
        return DEFAULT_CHECKPOINT_URLS.get(checkpoint_name)

    def _download_checkpoint(self, source_url: str, destination: Path) -> str | None:
        """Download a checkpoint file to destination with an atomic replace."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        temp_path = destination.with_suffix(f"{destination.suffix}.download")

        try:
            timeout_seconds = max(1, int(self._settings.model_download_timeout_seconds))
            request = Request(source_url, headers={"User-Agent": "AI-Image-Enhancement-System/1.0"})
            with urlopen(request, timeout=timeout_seconds) as response, temp_path.open("wb") as target:
                shutil.copyfileobj(response, target)
            temp_path.replace(destination)
            logger.info("Downloaded checkpoint from %s to %s.", source_url, destination)
            return None
        except Exception as exc:  # pragma: no cover - network/filesystem dependent
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            return str(exc)

    def _ensure_checkpoint(
        self,
        model_label: str,
        checkpoint_name: str,
        configured_url: str | None,
    ) -> tuple[Path | None, str | None]:
        """Return checkpoint path, downloading it when enabled and necessary."""
        model_path = self._settings.resolved_weights_dir / checkpoint_name
        if model_path.exists():
            return model_path, None

        if not self._settings.model_auto_download:
            return None, (
                f"Missing {model_label} checkpoint: {model_path}. "
                "Enable MODEL_AUTO_DOWNLOAD=true or place the file manually."
            )

        source_url = self._resolve_checkpoint_url(checkpoint_name, configured_url)
        if not source_url:
            return None, (
                f"Missing {model_label} checkpoint: {model_path}. "
                "No download URL is configured."
            )

        logger.info("Checkpoint %s not found. Downloading from %s.", checkpoint_name, source_url)
        download_error = self._download_checkpoint(source_url, model_path)
        if download_error:
            return None, (
                f"Missing {model_label} checkpoint: {model_path}. "
                f"Auto-download failed: {download_error}"
            )

        if not model_path.exists():
            return None, (
                f"Missing {model_label} checkpoint: {model_path}. "
                "Download completed without creating the target file."
            )

        return model_path, None

    def _load_gfpgan(self) -> tuple[Any | None, str | None]:
        """Load GFPGAN model from configured checkpoint path."""
        model_path, checkpoint_error = self._ensure_checkpoint(
            model_label="GFPGAN",
            checkpoint_name=self._settings.model_checkpoint_gfpgan,
            configured_url=self._settings.model_checkpoint_gfpgan_url,
        )
        if checkpoint_error:
            return None, checkpoint_error

        try:
            _ensure_torchvision_compat()
            import torch
            from gfpgan import GFPGANer

            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = GFPGANer(
                model_path=str(model_path),
                upscale=1,
                arch="clean",
                channel_multiplier=2,
                bg_upsampler=None,
                device=device,
            )
            return model, None
        except Exception as exc:  # pragma: no cover - depends on local ML runtime
            return None, f"GFPGAN unavailable: {exc}"

    def _load_realesrgan(self) -> tuple[Any | None, str | None]:
        """Load Real-ESRGAN model from configured checkpoint path."""
        model_path, checkpoint_error = self._ensure_checkpoint(
            model_label="Real-ESRGAN",
            checkpoint_name=self._settings.model_checkpoint_realesrgan,
            configured_url=self._settings.model_checkpoint_realesrgan_url,
        )
        if checkpoint_error:
            return None, checkpoint_error

        try:
            _ensure_torchvision_compat()
            import torch
            from realesrgan import RealESRGANer

            network = self._build_realesrgan_network(self._settings.model_checkpoint_realesrgan)
            use_fp16 = bool(torch.cuda.is_available() and self._settings.fp16_default)

            model = RealESRGANer(
                scale=self._settings.scale_factor,
                model_path=str(model_path),
                model=network,
                tile=self._settings.tile_size,
                tile_pad=self._settings.tile_pad,
                pre_pad=self._settings.pre_pad,
                half=use_fp16,
            )
            return model, None
        except Exception as exc:  # pragma: no cover - depends on local ML runtime
            return None, f"Real-ESRGAN unavailable: {exc}"

    @staticmethod
    def _build_realesrgan_network(checkpoint_name: str) -> Any:
        """Build Real-ESRGAN network architecture based on checkpoint naming."""
        lowered = checkpoint_name.lower()
        if "general" in lowered:
            from realesrgan.archs.srvgg_arch import SRVGGNetCompact

            return SRVGGNetCompact(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_conv=32,
                upscale=4,
                act_type="prelu",
            )

        from basicsr.archs.rrdbnet_arch import RRDBNet

        return RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
            num_grow_ch=32,
            scale=4,
        )


def checkpoint_exists(path: Path) -> bool:
    """Return True when a checkpoint file exists on disk."""
    return path.exists() and path.is_file()
