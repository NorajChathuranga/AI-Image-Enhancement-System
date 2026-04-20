<div align="center">

# 🖼️ AI Image Enhancer

**Full-Stack Deep Learning Image Enhancement System**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1+-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

*Enhance low-quality images using Real-ESRGAN super-resolution and GFPGAN face restoration — served through a clean React UI with async job processing.*

[**Live Demo**](#deployment) · [**Quick Start**](#quick-start) · [**API Docs**](#api-reference) · [**Build Plan**](#build-phases)

---

</div>

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Super Resolution** | 4× upscaling via Real-ESRGAN — GAN-based texture synthesis |
| 👤 **Face Restoration** | GFPGAN reconstructs facial structure and sharpens features |
| 🔇 **Denoising** | OpenCV-based noise reduction as preprocessing step |
| ⚡ **Async Processing** | Non-blocking job queue — upload and poll, no page freeze |
| 📊 **Job History** | SQLite-backed job log with per-stage processing times |
| 🖼️ **Before/After Slider** | Interactive comparison viewer in the React frontend |
| 🗜️ **WebP Output** | ~30% smaller output files at equivalent visual quality |
| 🛡️ **Security Hardened** | MIME validation, UUID filenames, rate limiting, auto-cleanup |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│   Upload → Progress Bar → Before/After Slider → Download │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP (REST)
┌──────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend                        │
│   POST /enhance → job_id  │  GET /status  │  GET /result │
└──────────────────────┬──────────────────────────────────┘
                       │ BackgroundTasks
┌──────────────────────▼──────────────────────────────────┐
│                  AI Pipeline                             │
│  Validate → Denoise → Deblur → GFPGAN → Real-ESRGAN     │
└──────────────────────┬──────────────────────────────────┘
                       │
          ┌────────────┴───────────┐
          │                        │
    ┌─────▼──────┐         ┌───────▼──────┐
    │  SQLite DB  │         │  File Storage │
    │  Job Logs   │         │  WebP Output  │
    └────────────┘         └──────────────┘
```

### Processing Pipeline

```
Input Image
    │
    ▼
① Validation      ← MIME type check, size limit (10MB max)
    │
    ▼
② Denoising       ← OpenCV fastNlMeansDenoisingColored
    │
    ▼
③ Deblurring      ← OpenCV Gaussian sharpening kernel
    │
    ▼
④ Face Detection  ← GFPGAN internal face detector
    │
    ▼
⑤ Face Enhance    ← GFPGAN v1.3 restoration
    │
    ▼
⑥ Super-Res       ← Real-ESRGAN 4× (tile=512 to prevent OOM)
    │
    ▼
WebP Output       ← Pillow, quality=90, ~30% smaller than PNG
```

---

## 📁 Project Structure

```
ai-image-enhancer/
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + lifespan model loading
│   │   ├── api/
│   │   │   └── routes.py        # /enhance, /status, /result, /jobs
│   │   ├── pipeline/
│   │   │   ├── validator.py     # MIME type + size validation
│   │   │   ├── preprocessor.py  # Denoise + deblur (OpenCV)
│   │   │   ├── face_enhancer.py # GFPGAN inference
│   │   │   ├── upscaler.py      # Real-ESRGAN inference (tile=512)
│   │   │   └── orchestrator.py  # Wires all stages together
│   │   ├── models/
│   │   │   └── job.py           # SQLModel Job schema
│   │   └── database.py          # SQLite connection + session
│   ├── weights/                 # Downloaded model weights (gitignored)
│   ├── temp/                    # Incoming uploads (gitignored)
│   ├── output/                  # Enhanced images (gitignored)
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── UploadZone.jsx   # react-dropzone drag-and-drop
│   │   │   ├── ProgressBar.jsx  # Polls /status every 2s
│   │   │   ├── CompareSlider.jsx # react-compare-image
│   │   │   └── DownloadButton.jsx
│   │   └── api.js               # All fetch calls (single source of truth)
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (recommended)
- ~4GB free disk space (model weights)

### Option A — Docker Compose (Recommended)

```bash
git clone https://github.com/yourusername/ai-image-enhancer.git
cd ai-image-enhancer

docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option B — Manual Setup

**Backend**

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env: set TORCH_HOME to an absolute path for model caching

# Run server
uvicorn app.main:app --reload --port 8000
```

**Frontend**

```bash
cd frontend

npm install
cp .env.example .env.local
# Edit .env.local: set VITE_API_URL=http://localhost:8000

npm run dev
```

> **First startup note:** On first run, GFPGAN helper files (`detection_Resnet50_Final.pth`, `parsing_parsenet.pth`) can auto-download if internet is available. Main checkpoints (`realesr-general-x4v3.pth`, `GFPGANv1.3.pth`) must already exist in `backend/weights/`.

---

## ⚙️ Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `TORCH_HOME` | `./weights` | Directory for cached model weights |
| `MAX_UPLOAD_MB` | `10` | Maximum upload file size in megabytes |
| `RATE_LIMIT` | `10/minute` | Max requests per IP per minute |
| `CLEANUP_HOURS` | `1` | Delete temp/output files older than N hours |
| `DATABASE_URL` | `sqlite:///./jobs.db` | SQLite database path |

### Frontend (`frontend/.env.local`)

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Backend API base URL |
| `VITE_POLL_INTERVAL_MS` | `2000` | Job status polling interval |

---

## 📡 API Reference

### Submit Enhancement Job

```http
POST /v1/enhance
Content-Type: multipart/form-data

file: <image file>
```

```json
// Response 202
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending"
}
```

### Poll Job Status

```http
GET /v1/status/{job_id}
```

```json
// Response 200
{
  "job_id": "550e8400-...",
  "status": "processing",        // pending | processing | complete | failed
  "progress_pct": 65,
  "processing_time_ms": null,    // populated when complete
  "error": null                  // populated when failed
}
```

### Download Result

```http
GET /v1/result/{job_id}
```

Returns the enhanced image as a `image/webp` stream.

### Job History

```http
GET /v1/jobs?limit=20
```

```json
{
  "jobs": [
    {
      "job_id": "550e8400-...",
      "status": "complete",
      "input_filename": "photo.jpg",
      "input_size_bytes": 2048576,
      "processing_time_ms": 4823,
      "created_at": "2025-04-19T10:30:00Z",
      "completed_at": "2025-04-19T10:30:05Z"
    }
  ]
}
```

### Health Check

```http
GET /health
```

```json
{
  "status": "ok",
  "models_loaded": true,
  "uptime_seconds": 3620
}
```

---

## ⚡ Performance

| Image Size | CPU (no tiling) | CPU (tile=512) | GPU — T4 |
|---|---|---|---|
| 512 × 512 | 2–3s | 2–3s | < 0.5s |
| 1080p | 5–10s | 5–8s | 1–2s |
| 4K | OOM crash | 15–20s | 3–5s |

> Tiling (`tile=512`) is enabled by default. GPU times are measured on HuggingFace Spaces free T4 tier.

---

## 🚢 Deployment

### Backend — HuggingFace Spaces (Free GPU)

1. Create a Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Select **Docker** SDK and **T4-small** hardware (free tier)
3. Add `backend/Dockerfile` — uses `nvidia/cuda` base image
4. Push backend to the Space repository via `git`
5. Set `TORCH_HOME=/app/weights` in Space settings → Secrets

```bash
# Push to HuggingFace Space
git remote add hf https://huggingface.co/spaces/yourusername/ai-image-enhancer
git subtree push --prefix backend hf main
```

### Frontend — Vercel (Free)

1. Import the repository at [vercel.com](https://vercel.com)
2. Set root directory to `frontend`
3. Add environment variable: `VITE_API_URL=https://yourusername-ai-image-enhancer.hf.space`
4. Deploy — Vercel auto-builds on every push to `main`

> **HuggingFace cold starts:** Free Spaces sleep after 48h of inactivity. The first request after sleep takes 30–60 seconds to wake. Normal behaviour on the free tier.

---

## 🛡️ Security

- **MIME validation** — `python-magic` checks actual file content, not just extension
- **UUID filenames** — output files never use client-provided names (prevents path traversal)
- **Rate limiting** — `slowapi` enforces 10 requests/IP/minute (HTTP 429 on breach)
- **Auto-cleanup** — temp and output files deleted after 1 hour via background scheduler
- **Size limit** — 10MB maximum upload enforced before processing begins

---

## 📦 Dependencies

### Backend

| Package | Version | Purpose |
|---|---|---|
| fastapi | ≥ 0.104 | Web framework |
| uvicorn | ≥ 0.24 | ASGI server |
| torch + torchvision | ≥ 2.1 | Deep learning runtime |
| realesrgan | ≥ 0.3 | Super-resolution model |
| gfpgan | ≥ 1.3 | Face restoration model |
| basicsr | ≥ 1.4.2 | Real-ESRGAN dependency |
| opencv-python-headless | ≥ 4.8 | Denoising + deblurring |
| pillow | ≥ 10.0 | Image I/O and WebP output |
| sqlmodel | ≥ 0.0.14 | SQLite ORM |
| slowapi | ≥ 0.1.9 | Rate limiting |
| python-magic | ≥ 0.4.27 | MIME type validation |

### Frontend

| Package | Purpose |
|---|---|
| react + vite | UI framework + dev server |
| react-dropzone | Drag-and-drop upload zone |
| react-compare-image | Before/after slider |

---

## ⚠️ Known Limitations

- **Deblurring** is classical (no learned blur kernel estimation) — effectiveness is limited for heavy motion blur
- **CPU inference** is slow for images above 1080p; GPU deployment is strongly recommended
- **Face enhancement** only improves faces that GFPGAN's detector can locate — very small or occluded faces may be skipped
- **HuggingFace free tier** has usage limits and cold-start delays

---

## 🔭 Roadmap

- [ ] User authentication with JWT (FastAPI Users)
- [ ] Batch processing — ZIP upload with per-image results
- [ ] Model selection UI — Fast / Balanced / Max quality presets
- [ ] WebSocket progress instead of polling
- [ ] Cloudflare R2 cloud storage (10GB free tier)
- [ ] CodeFormer integration as alternative face restoration model

---

## 📚 References

- Wang, X. et al. (2021). [Real-ESRGAN: Training Real-World Blind Super-Resolution with Pure Synthetic Data](https://arxiv.org/abs/2107.10833). ICCV 2021 Workshop.
- Wang, X. et al. (2021). [GFPGAN: Towards Real-World Blind Face Restoration with Generative Facial Prior](https://arxiv.org/abs/2101.04061). CVPR 2021.
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [HuggingFace Spaces — Docker SDK](https://huggingface.co/docs/hub/spaces-sdks-docker)

---

## 👨‍💻 Author

**Noraj Chathuranga Pradeepa**
Faculty of Technology, Rajarata University of Sri Lanka
Bachelor of Information and Communication Technology (Hons)

---

<div align="center">

Made with ☕ and way too many GPU hours

</div>
