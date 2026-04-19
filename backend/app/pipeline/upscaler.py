from __future__ import annotations

import logging
from typing import Any

import cv2
import numpy as np


logger = logging.getLogger(__name__)


def upscale(image: np.ndarray, realesrgan_model: Any | None, scale_factor: int = 4) -> np.ndarray:
    """Upscale an image with Real-ESRGAN or bicubic fallback."""
    if realesrgan_model is None:
        height, width = image.shape[:2]
        return cv2.resize(
            image,
            (width * scale_factor, height * scale_factor),
            interpolation=cv2.INTER_CUBIC,
        )

    try:
        enhanced, _ = realesrgan_model.enhance(image, outscale=scale_factor)
        return enhanced
    except Exception:
        logger.exception("Real-ESRGAN upscaling failed, using bicubic fallback.")
        height, width = image.shape[:2]
        return cv2.resize(
            image,
            (width * scale_factor, height * scale_factor),
            interpolation=cv2.INTER_CUBIC,
        )
