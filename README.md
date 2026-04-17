# 🚀 AI Image Enhancement System

> A full-stack AI-powered image enhancement platform built with a **monorepo architecture**, combining a React frontend and FastAPI backend with deep learning models for real-world image processing.

---

## 📸 Overview

This project delivers a **production-ready AI service** that enhances low-quality images using a modular deep learning pipeline.

It integrates:

* Super-resolution (Real-ESRGAN)
* Face restoration (GFPGAN)
* Image preprocessing (denoise, deblur)

The system is designed for **scalability, maintainability, and real-world deployment**.

---

## 🧠 Key Features

* 🖼️ AI Image Upscaling (2x / 4x)
* 🙂 Face Enhancement (GFPGAN)
* 🧹 Noise Reduction
* ⚡ Modular Processing Pipeline
* 🔄 Before/After Comparison Slider
* 📤 Drag & Drop Upload UI
* ⏳ Processing Feedback (Loader)
* 📥 Download Enhanced Image
* 🌐 REST API (FastAPI)
* 🧱 Monorepo Architecture

---

## 🏗️ Architecture

### 🔷 Monorepo Structure

```
ai-image-enhancer/
├── frontend/   # React (UI)
├── backend/    # FastAPI + AI pipeline
└── docker-compose.yml
```

---

### 🔷 System Flow

```
Frontend (React UI)
        ↓ HTTP Request
Backend (FastAPI API)
        ↓
AI Processing Pipeline
        ↓
Enhanced Image Output
```

---

### 🔷 Processing Pipeline

```
Upload Image
    ↓
Validation
    ↓
Denoise
    ↓
Deblur (optional)
    ↓
Face Detection
    ↓
Face Enhancement (GFPGAN)
    ↓
Super Resolution (Real-ESRGAN)
    ↓
Output Image
```

---

## 🧱 Tech Stack

### 🔹 Frontend

* React (Vite)
* Axios
* React Dropzone
* React Compare Slider

### 🔹 Backend

* FastAPI
* Python

### 🔹 AI / ML

* PyTorch
* Real-ESRGAN
* GFPGAN

### 🔹 Image Processing

* OpenCV
* Pillow

### 🔹 DevOps

* Docker
* Docker Compose

---

## 📂 Project Structure

```
ai-image-enhancer/
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── app/
│   ├── models/
│   ├── temp/
│   ├── output/
│   └── requirements.txt
│
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Setup & Installation

### 1️⃣ Clone Repository

```
git clone https://github.com/your-username/ai-image-enhancer.git
cd ai-image-enhancer
```

---

### 2️⃣ Run Backend

```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

### 3️⃣ Run Frontend

```
cd frontend
npm install
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

Backend runs at:

```
http://127.0.0.1:8000
```

---

## 🐳 Run with Docker (Recommended)

```
docker-compose up --build
```

---

## 📡 API Documentation

### 🔹 Endpoint

```
POST /api/enhance
```

### 🔹 Request

* `multipart/form-data`
* key: `image`

### 🔹 Response

```json
{
  "status": "success",
  "processing_time": "4.2s",
  "image_url": "/output/{id}.png"
}
```

---

## ⚡ Performance

| Image Size | CPU Time  |
| ---------- | --------- |
| 512x512    | ~2–3 sec  |
| 1080p      | ~5–10 sec |
| 4K         | ~15+ sec  |

> ⚠️ GPU significantly improves performance

---

## ⚠️ Limitations

* Cannot reconstruct completely lost image data
* Limited performance on CPU
* Deblurring effectiveness is partial
* Large images increase processing time

---

## 🚀 Future Improvements

* GPU acceleration
* Batch processing
* Real-time enhancement
* User authentication system
* Cloud deployment (scaling)
* Advanced restoration models

---

## 💼 Use Cases

* Old photo restoration
* Social media image enhancement
* E-commerce product images
* CCTV frame enhancement
* Document clarity improvement

---

## 🔐 Security

* File validation (type & size)
* Safe file handling
* No persistent sensitive data storage

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📄 License

MIT License

---

## 👨‍💻 Author

**Noraj Chathuranga Pradeepa**
Full-Stack Developer | AI Engineer

---

## ⭐ Support

If you find this project useful, give it a ⭐ on GitHub!
