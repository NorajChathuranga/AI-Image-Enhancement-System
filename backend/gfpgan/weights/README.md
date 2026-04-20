# GFPGAN Helper Weights

This folder stores FaceXLib helper models used by GFPGAN for face detection and face parsing.

## Files In This Folder

- `detection_Resnet50_Final.pth`: face detection model.
- `parsing_parsenet.pth`: face parsing/segmentation model.

## Auto Download Behavior

These two helper files are downloaded automatically on first GFPGAN load **if internet is available**.

The backend triggers model loading on startup in `backend/app/main.py`, and GFPGAN internally fetches these files when missing.

## Main Checkpoint Auto Download

Main checkpoints in `backend/weights/` are now auto-downloaded when missing (if internet is available):

- `realesr-general-x4v3.pth`
- `GFPGANv1.3.pth`

Default source URLs are built into `backend/app/services/model_service.py`.

Optional overrides in `backend/.env`:

- `MODEL_AUTO_DOWNLOAD=true`
- `MODEL_DOWNLOAD_TIMEOUT_SECONDS=600`
- `MODEL_CHECKPOINT_REALESRGAN_URL=`
- `MODEL_CHECKPOINT_GFPGAN_URL=`

## What Is Still Manual (Offline / Blocked Network)

If network access is blocked, you must copy all required files manually.

## Manual Setup (Offline / Restricted Network)

1. Create/verify `backend/weights/`.
2. Put the two primary checkpoints in `backend/weights/` with exact names:
   - `realesr-general-x4v3.pth`
   - `GFPGANv1.3.pth`
3. Put the two helper files in this folder (`backend/gfpgan/weights/`) with exact names:
   - `detection_Resnet50_Final.pth`
   - `parsing_parsenet.pth`
4. Set `MODEL_AUTO_DOWNLOAD=false` in `backend/.env` to avoid startup download attempts.
5. Confirm `MODEL_CHECKPOINT_GFPGAN=GFPGANv1.3.pth` in `backend/.env`.
6. Confirm `MODEL_CHECKPOINT_REALESRGAN=realesr-general-x4v3.pth` in `backend/.env`.
7. Start backend and verify `GET /health` returns `models_loaded: true`.

## Notes

- Keep original checkpoint filenames and update `.env` instead of renaming model files.
- If you switch checkpoint version, update `ai-model/models/README.md` to keep the version registry accurate.
