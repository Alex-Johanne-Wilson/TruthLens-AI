# ai_detection/api/main.py
"""FastAPI application entry point for TruthLens AI.
Provides health, image analysis, deepfake analysis, and document analysis endpoints.
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .dependencies import get_image_model, get_deepfake_model
from .routes import health, image, deepfake, document

# Ensure output directories exist
gradcam_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "api", "gradcam"))
os.makedirs(gradcam_dir, exist_ok=True)

ela_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "api", "ela"))
os.makedirs(ela_dir, exist_ok=True)

app = FastAPI(title="TruthLens AI Backend", version="1.0.0")

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models at startup
@app.on_event("startup")
async def startup_event():
    # Models are cached in module-level variables via dependencies
    get_image_model()
    get_deepfake_model()

# Mount static files for Grad-CAM results and ELA results
app.mount("/static/gradcam", StaticFiles(directory=gradcam_dir), name="gradcam")
app.mount("/static/ela", StaticFiles(directory=ela_dir), name="ela")

# Include routers
app.include_router(health.router)
app.include_router(image.router, prefix="/api/analyze")
app.include_router(deepfake.router, prefix="/api/analyze")
app.include_router(document.router, prefix="/api/analyze")
