from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import cv2
from PIL import Image

from app.pipeline.face_enhancer import enhance_faces
from app.pipeline.preprocessor import deblur, denoise
from app.pipeline.upscaler import upscale
from app.services.model_service import ModelRuntime


@dataclass
class PipelineResult:
    """Result payload from orchestrated image processing pipeline."""

    output_path: Path
    total_time_ms: int
    stage_times_ms: dict[str, int]


def run_pipeline(
    input_path: Path,
    output_path: Path,
    runtime: ModelRuntime,
    scale_factor: int,
    denoise_enabled: bool = True,
    deblur_enabled: bool = True,
    face_enhance_enabled: bool = True,
    output_quality: int = 88,
    progress_callback: Callable[[int, str], None] | None = None,
) -> PipelineResult:
    """Run image pipeline and persist final WebP output."""
    stage_times: dict[str, int] = {}
    total_start = time.perf_counter()

    def mark_progress(percent: int, stage: str) -> None:
        if progress_callback:
            progress_callback(percent, stage)

    mark_progress(10, "decode")
    decode_start = time.perf_counter()
    image = cv2.imread(str(input_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode the input image.")
    stage_times["decode"] = int((time.perf_counter() - decode_start) * 1000)

    mark_progress(30, "denoise" if denoise_enabled else "denoise_skipped")
    denoise_start = time.perf_counter()
    if denoise_enabled:
        image = denoise(image)
    stage_times["denoise"] = int((time.perf_counter() - denoise_start) * 1000)

    mark_progress(40, "deblur" if deblur_enabled else "deblur_skipped")
    deblur_start = time.perf_counter()
    if deblur_enabled:
        image = deblur(image)
    stage_times["deblur"] = int((time.perf_counter() - deblur_start) * 1000)
    stage_times["preprocess"] = stage_times["denoise"] + stage_times["deblur"]

    mark_progress(50, "face_enhance" if face_enhance_enabled else "face_enhance_skipped")
    face_start = time.perf_counter()
    if face_enhance_enabled:
        image = enhance_faces(image, runtime.gfpgan_model)
    stage_times["face_enhance"] = int((time.perf_counter() - face_start) * 1000)

    mark_progress(75, "super_resolution")
    upscale_start = time.perf_counter()
    image = upscale(image, runtime.realesrgan_model, scale_factor=scale_factor)
    stage_times["super_resolution"] = int((time.perf_counter() - upscale_start) * 1000)

    mark_progress(90, "encode_webp")
    encode_start = time.perf_counter()
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    normalized_quality = max(1, min(100, output_quality))
    Image.fromarray(rgb_image).save(
        output_path,
        format="WEBP",
        quality=normalized_quality,
        method=2,
    )
    stage_times["encode_webp"] = int((time.perf_counter() - encode_start) * 1000)

    mark_progress(100, "complete")
    total_time_ms = int((time.perf_counter() - total_start) * 1000)

    return PipelineResult(
        output_path=output_path,
        total_time_ms=total_time_ms,
        stage_times_ms=stage_times,
    )
