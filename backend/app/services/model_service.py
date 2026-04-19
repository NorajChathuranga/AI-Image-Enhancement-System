from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import Settings


logger = logging.getLogger(__name__)


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

    def _load_gfpgan(self) -> tuple[Any | None, str | None]:
        """Load GFPGAN model from configured checkpoint path."""
        model_path = self._settings.resolved_weights_dir / self._settings.model_checkpoint_gfpgan
        if not model_path.exists():
            return None, f"Missing GFPGAN checkpoint: {model_path}"

        try:
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
        model_path = self._settings.resolved_weights_dir / self._settings.model_checkpoint_realesrgan
        if not model_path.exists():
            return None, f"Missing Real-ESRGAN checkpoint: {model_path}"

        try:
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
