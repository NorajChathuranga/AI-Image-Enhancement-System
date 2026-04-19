from __future__ import annotations

import cv2
import numpy as np


def denoise(image: np.ndarray) -> np.ndarray:
    """Apply color denoising using OpenCV fast non-local means."""
    return cv2.fastNlMeansDenoisingColored(image, None, 7, 7, 7, 21)


def deblur(image: np.ndarray) -> np.ndarray:
    """Apply lightweight sharpening kernel to reduce mild blur."""
    kernel = np.array(
        [
            [-1.0, -1.0, -1.0],
            [-1.0, 9.0, -1.0],
            [-1.0, -1.0, -1.0],
        ],
        dtype=np.float32,
    )
    return cv2.filter2D(image, -1, kernel)


def preprocess(image: np.ndarray) -> np.ndarray:
    """Run preprocessing stages in sequence."""
    denoised = denoise(image)
    return deblur(denoised)
