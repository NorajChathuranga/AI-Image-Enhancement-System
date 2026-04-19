from __future__ import annotations

import numpy as np

from app.pipeline.preprocessor import preprocess


def test_preprocess_returns_same_shape_and_dtype() -> None:
    image = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)

    output = preprocess(image)

    assert output.shape == image.shape
    assert output.dtype == image.dtype


def test_preprocess_handles_large_images() -> None:
    image = np.random.randint(0, 255, (1300, 1700, 3), dtype=np.uint8)

    output = preprocess(image)

    assert output.shape == image.shape