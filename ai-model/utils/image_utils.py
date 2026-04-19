from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def read_image(path: Path) -> np.ndarray:
    """Read an image from disk in BGR format."""
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Unable to read image at {path}")
    return image


def save_webp(path: Path, image_bgr: np.ndarray, quality: int = 90) -> Path:
    """Save an image array as WebP format."""
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image_rgb).save(path, format="WEBP", quality=quality)
    return path
