# Model Checkpoint Registry

This file tracks checkpoint filenames and versions for reproducibility.

| Model | Version | Filename | Scale | Notes |
|---|---|---|---|---|
| Real-ESRGAN | realesr-general-x4v3 | realesr-general-x4v3.pth | x4 | Default for mixed photo and illustration content |
| Real-ESRGAN | realesrgan-x4plus | RealESRGAN_x4plus.pth | x4 | Alternative profile optimized for photographic detail |
| GFPGAN | v1.4 | GFPGANv1.4.pth | n/a | Face restoration checkpoint |

## Change Log

- 2026-04-19: Initial registry created.

## Backup Rule

Always copy existing checkpoints to a timestamped backup before replacement.
