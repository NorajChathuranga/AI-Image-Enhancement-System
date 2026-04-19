from __future__ import annotations

import logging
from typing import Any

import numpy as np


logger = logging.getLogger(__name__)


def enhance_faces(image: np.ndarray, gfpgan_model: Any | None) -> np.ndarray:
    """Enhance detected faces with GFPGAN when model is available."""
    if gfpgan_model is None:
        return image

    try:
        _, _, restored = gfpgan_model.enhance(
            image,
            has_aligned=False,
            only_center_face=False,
            paste_back=True,
        )
        if restored is None:
            return image
        return restored
    except Exception:
        logger.exception("GFPGAN enhancement failed, returning original frame.")
        return image
