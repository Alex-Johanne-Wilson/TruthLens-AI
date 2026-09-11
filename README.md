# TruthLens AI

> **An Explainable Digital Evidence Integrity & Trust Assessment Framework**

TruthLens AI is a modular cyber-forensics platform engineered to assess the integrity, authenticity, and manipulation characteristics of digital evidence (images, videos, and documents).

---

## 🎯 Current Completed Functionality (Checkpoint 1)

* **AI-Generated vs. Real Image Detection**: Deep convolutional inference using transfer-learned **EfficientNet-B0**.
* **Trained Model Checkpoint**: Evaluated model checkpoint weights (`best_model.pth`, ~46.35 MB).
* **Explainable AI (Grad-CAM)**: Heatmap visualization mapping the convolutional activations that influenced the classification verdict.
* **FastAPI Backend Service**: Real-time REST API serving `/health`, `/api/analyze/image`, and `/api/analyze/deepfake`.
* **Cyber-Forensics Frontend**: React/Vite web application featuring a dark cyber-forensics UI, interactive evidence upload zone, classification cards, and side-by-side Grad-CAM inspector.
* **Full End-to-End Integration**: Real-time communication between browser client and FastAPI model service.

---

## 🔬 Verified Image Analysis Pipeline

The end-to-end inference flow has been verified:

$$\text{Image Upload} \longrightarrow \text{FastAPI REST} \longrightarrow \text{EfficientNet-B0} \longrightarrow \text{Prediction} \longrightarrow \text{Probabilities} \longrightarrow \text{Grad-CAM} \longrightarrow \text{React UI}$$

### Verification Test Case

* **Test Image**: `data/train/real/real_0001.jpg`
* **Prediction**: `REAL`
* **AI-Generated Probability**: $\approx 0.00187\%$ (`1.8726996e-05`)
* **Real Probability**: $\approx 99.99813\%$ (`0.99998128`)
* **Confidence**: $\approx 99.99813\%$
* **Grad-CAM Artifact**: Successfully synthesized and served over `/static/gradcam/gradcam_real_0001.png`

> **Note**: These metrics are evaluated against the specific benchmark dataset and do not represent general real-world accuracy across arbitrary in-the-wild distributions.

---

## 🧠 Model Architecture & Evaluation

| Parameter | Specification |
| :--- | :--- |
| **Base Architecture** | EfficientNet-B0 (Pretrained on ImageNet-1K) |
| **Input Dimensions** | $224 \times 224 \times 3$ RGB |
| **Class 0** | `ai_generated` |
| **Class 1** | `real` |
| **Random Seed** | 42 |
| **Best Validation F1** | $\approx 0.9894$ |
| **Held-Out Test Accuracy** | $\approx 99.07\%$ |
| **Test ROC-AUC** | $\approx 99.93\%$ |

*Disclaimer: Performance statistics reflect evaluation on the curated benchmark dataset (see below) and should not be construed as a universal guarantee against novel diffusion models, adversarial samples, or post-processed social media uploads.*

---

## 📊 Dataset Information

* **Source**: `Parveshiiii/AI-vs-Real` (Hugging Face)
* **Configuration**: 5,000 balanced images (2,500 real / 2,500 synthetic)
* **Split Configuration**:
  * **Train**: 3,500 images (1,750 real / 1,750 synthetic)
  * **Validation**: 750 images (375 real / 375 synthetic)
  * **Test**: 750 images (375 real / 375 synthetic)
* **Metadata**: Full split and class indices are documented in [`ai_detection/data/dataset_info.json`](file:///C:/Users/Alex%20Wilson/OneDrive/Documents/A.Projects/Truthlens-AI/ai_detection/data/dataset_info.json).

*Note: Raw images are excluded from version control via `.gitignore` to maintain a lightweight repository. To re-download or inspect the data, refer to `dataset_info.json` and the extraction scripts.*

---

## 📋 Project Status Matrix

### ✅ Completed & Verified

* [x] Benchmark dataset curation and metadata logging
* [x] AI image detector fine-tuning (EfficientNet-B0)
* [x] Test-set evaluation and metrics calculation
* [x] Explainable AI Grad-CAM generation pipeline
* [x] FastAPI REST endpoints (`/health`, `/api/analyze/image`)
* [x] Cyber-forensics React/Vite user interface
* [x] Client-Server integration & dynamic probability display
* [x] Production build verification (`npm run build`)

### 🚧 Prototype / Pending Integration

* [ ] **Deepfake Detection**: Prototype pipeline scaffolded (`/api/analyze/deepfake`). *Model is currently untrained and unvalidated.*
* [ ] **EXIF & Hex Metadata Extraction**
* [ ] **Error Level Analysis (ELA)**
* [ ] **Copy-Move Forgery Detection (Keypoints/Blocks)**
* [ ] **JPEG Double Compression Forensics**
* [ ] **Shadow / Illumination Inconsistency Analysis**
* [ ] **Screen Recapture & Moiré Pattern Detection**
* [ ] **Unified Digital Evidence Trust Score Algorithm**
* [ ] **Courtroom-Ready PDF Forensic Evidence Export**

---

## 🚀 Quick Start Guide

### Prerequisites

* Python 3.10+
* Node.js 18+ and npm

### 1. Start the Backend API

```bash
cd ai_detection
pip install -r requirements.txt
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Verify backend health:

```bash
curl http://127.0.0.1:8000/health
# Expected: {"status":"ok"}
```

### 2. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Access URLs

* **TruthLens Frontend UI**: [http://127.0.0.1:5173](http://127.0.0.1:5173)
* **FastAPI Interactive Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **FastAPI Health Route**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 👥 Repository Structure

```text
Truthlens-AI/
├── ai_detection/              # Python AI backend & ML pipelines
│   ├── api/                   # FastAPI application & REST routes
│   │   ├── routes/            # Route handlers (health, image, deepfake)
│   │   ├── dependencies.py    # Model caching and dependencies
│   │   ├── main.py            # FastAPI entrypoint & CORS config
│   │   └── schemas.py         # Pydantic request/response schemas
│   ├── data/                  # Dataset info (images gitignored)
│   │   └── dataset_info.json  # Dataset provenance & split counts
│   ├── outputs/               # Checkpoints & evaluation metrics
│   │   └── checkpoints/       # Trained weights (best_model.pth)
│   ├── src/                   # PyTorch dataset, model, and Grad-CAM logic
│   └── requirements.txt       # Python dependencies
├── frontend/                  # React + Vite application
│   ├── src/                   # React components & services
│   ├── index.html             # Entry HTML
│   ├── package.json           # Node scripts & dependencies
│   └── vite.config.js         # Vite dev proxy configuration
├── .gitignore                 # Excludes environments, caches, node_modules
└── README.md                  # Project documentation & status
```
