from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest


def load_metrics_module():
    """Load metrics module from path because ai-model is not a valid package name."""
    metrics_path = Path(__file__).resolve().parents[1] / "utils" / "metrics.py"
    spec = importlib.util.spec_from_file_location("metrics_module", metrics_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load metrics module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


metrics = load_metrics_module()
calculate_psnr = metrics.calculate_psnr
calculate_ssim = metrics.calculate_ssim


def test_metrics_happy_path_identical_images() -> None:
    """PSNR and SSIM should indicate perfect similarity for identical images."""
    image = np.zeros((16, 16, 3), dtype=np.uint8)
    psnr = calculate_psnr(image, image)
    ssim = calculate_ssim(image, image)
    assert psnr == float("inf")
    assert 0.99 <= ssim <= 1.0


def test_metrics_edge_case_large_image() -> None:
    """Metric computation should handle larger arrays without failure."""
    image_a = np.full((512, 512, 3), 120, dtype=np.uint8)
    image_b = np.full((512, 512, 3), 125, dtype=np.uint8)
    assert calculate_psnr(image_a, image_b) > 20


def test_metrics_error_case_shape_mismatch() -> None:
    """Metric functions should reject mismatched shapes."""
    image_a = np.zeros((8, 8, 3), dtype=np.uint8)
    image_b = np.zeros((8, 8), dtype=np.uint8)
    with pytest.raises(ValueError):
        calculate_psnr(image_a, image_b)
