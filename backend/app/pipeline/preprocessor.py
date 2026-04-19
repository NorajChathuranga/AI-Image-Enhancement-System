from __future__ import annotations

import cv2
import numpy as np


FAST_DENOISE_PIXEL_THRESHOLD = 2_000_000


def denoise(image: np.ndarray) -> np.ndarray:
    """Apply denoising with an adaptive strategy for large images."""
    height, width = image.shape[:2]
    if height * width > FAST_DENOISE_PIXEL_THRESHOLD:
        # Bilateral filtering is noticeably faster than fastNlMeans on large frames.
        return cv2.bilateralFilter(image, d=7, sigmaColor=35, sigmaSpace=35)

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
