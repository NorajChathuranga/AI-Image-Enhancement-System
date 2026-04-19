from __future__ import annotations

import numpy as np


def calculate_psnr(reference: np.ndarray, target: np.ndarray, max_value: float = 255.0) -> float:
    """Compute PSNR between reference and target images."""
    if reference.shape != target.shape:
        raise ValueError("Reference and target image shapes must match.")

    mse = np.mean((reference.astype(np.float32) - target.astype(np.float32)) ** 2)
    if mse == 0:
        return float("inf")
    return float(20 * np.log10(max_value / np.sqrt(mse)))


def calculate_ssim(reference: np.ndarray, target: np.ndarray) -> float:
    """Compute SSIM when available, otherwise return normalized fallback score."""
    if reference.shape != target.shape:
        raise ValueError("Reference and target image shapes must match.")

    try:
        from skimage.metrics import structural_similarity

        if reference.ndim == 3:
            value = structural_similarity(reference, target, channel_axis=2)
        else:
            value = structural_similarity(reference, target)
        return float(value)
    except Exception:
        reference_f = reference.astype(np.float32)
        target_f = target.astype(np.float32)
        mse = np.mean((reference_f - target_f) ** 2)
        score = 1.0 - min(1.0, mse / (255.0**2))
        return float(max(0.0, score))
