from __future__ import annotations

import importlib.util
from pathlib import Path

from PIL import Image
import pytest


def load_upscale_module():
    """Load upscale module from path because ai-model is not a valid package name."""
    module_path = Path(__file__).resolve().parents[1] / "inference" / "upscale.py"
    spec = importlib.util.spec_from_file_location("upscale_module", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load upscale module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


upscale_module = load_upscale_module()
UpscaleConfig = upscale_module.UpscaleConfig
upscale_image = upscale_module.upscale_image


def test_upscale_happy_path(tmp_path: Path) -> None:
    """Valid input image should be upscaled and saved as WebP."""
    source = tmp_path / "input.png"
    target = tmp_path / "output.webp"
    Image.new("RGB", (32, 32), color=(120, 30, 30)).save(source)

    result = upscale_image(source, target, model=None, config=UpscaleConfig(scale_factor=2))

    assert result.exists()
    with Image.open(result) as image:
        assert image.size == (64, 64)


def test_upscale_edge_case_large_image(tmp_path: Path) -> None:
    """Large image input should still process without exceptions."""
    source = tmp_path / "large.png"
    target = tmp_path / "large.webp"
    Image.new("RGB", (1024, 1024), color=(0, 80, 140)).save(source)

    result = upscale_image(source, target, model=None, config=UpscaleConfig(scale_factor=2))
    assert result.exists()


def test_upscale_error_case_corrupt_file(tmp_path: Path) -> None:
    """Corrupted files should raise a decode error."""
    source = tmp_path / "broken.png"
    target = tmp_path / "broken.webp"
    source.write_bytes(b"not-an-image")

    with pytest.raises(ValueError):
        upscale_image(source, target, model=None, config=UpscaleConfig(scale_factor=2))
