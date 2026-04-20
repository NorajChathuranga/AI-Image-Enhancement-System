# Model Checkpoint Registry

This file tracks checkpoint filenames and versions for reproducibility.

| Model | Version | Filename | Scale | Notes |
|---|---|---|---|---|
| Real-ESRGAN | realesr-general-x4v3 | realesr-general-x4v3.pth | x4 | Default for mixed photo and illustration content |
| Real-ESRGAN | realesrgan-x4plus | RealESRGAN_x4plus.pth | x4 | Alternative profile optimized for photographic detail |
| GFPGAN | v1.3 | GFPGANv1.3.pth | n/a | Active backend face restoration checkpoint |
| GFPGAN | v1.4 | GFPGANv1.4.pth | n/a | Optional checkpoint if configured in backend/.env |

## Change Log

- 2026-04-19: Initial registry created.
- 2026-04-20: Backend default checkpoint updated to GFPGANv1.3.pth and helper-weight setup documented.
- 2026-04-20: Added backend auto-download support for missing main checkpoints.

## Backend Auto Download

The backend can auto-download missing main checkpoints in `backend/weights/` when `MODEL_AUTO_DOWNLOAD=true`.

Default URL mapping currently covers:

- `GFPGANv1.3.pth`
- `realesr-general-x4v3.pth`

You can override sources with:

- `MODEL_CHECKPOINT_GFPGAN_URL`
- `MODEL_CHECKPOINT_REALESRGAN_URL`

## Backup Rule

Always copy existing checkpoints to a timestamped backup before replacement.
