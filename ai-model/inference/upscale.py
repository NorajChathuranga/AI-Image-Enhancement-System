from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
from PIL import Image


@dataclass
class UpscaleConfig:
    """Runtime settings for image upscaling."""

    scale_factor: int = 4
    tile_size: int = 512
    tile_pad: int = 10
    pre_pad: int = 0
    fp16: bool = True


def upscale_image(
    input_path: Path,
    output_path: Path,
    model: Any | None,
    config: UpscaleConfig,
) -> Path:
    """Upscale an input image and save WebP output."""
    frame = cv2.imread(str(input_path), cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Failed to decode input image.")

    if model is not None:
        enhanced, _ = model.enhance(frame, outscale=config.scale_factor)
        frame = enhanced
    else:
        height, width = frame.shape[:2]
        frame = cv2.resize(
            frame,
            (width * config.scale_factor, height * config.scale_factor),
            interpolation=cv2.INTER_CUBIC,
        )

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgb_frame).save(output_path, format="WEBP", quality=90)
    return output_path


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Upscale image with optional Real-ESRGAN model")
    parser.add_argument("input", type=Path, help="Input image path")
    parser.add_argument("output", type=Path, help="Output image path")
    parser.add_argument("--scale", type=int, default=4, choices=[2, 4], help="Upscale factor")
    return parser.parse_args()


def main() -> None:
    """Run CLI upscaling with fallback bicubic mode."""
    args = parse_args()
    config = UpscaleConfig(scale_factor=args.scale)
    upscale_image(args.input, args.output, model=None, config=config)


if __name__ == "__main__":
    main()
