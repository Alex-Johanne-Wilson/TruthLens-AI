# ai_detection/api/dependencies.py
"""Dependency utilities for FastAPI.
Loads the EfficientNet image model and tracks deepfake model readiness.
"""
import os
import torch
from pathlib import Path
from functools import lru_cache

# Image model loading
@lru_cache()
def get_image_model():
    from src.model import build_model
    checkpoint_path = Path(__file__).resolve().parents[1] / "outputs" / "checkpoints" / "best_model.pth"
    model = build_model(pretrained=False)
    checkpoint = torch.load(checkpoint_path, map_location=torch.device("cpu"))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model

# Deepfake model loading — only builds the architecture.
# Actual checkpoint loading is handled by inference.py which also
# reports whether the model is trained or not.
@lru_cache()
def get_deepfake_model():
    from src.deepfake.model import build_deepfake_model
    model = build_deepfake_model(pretrained=False)
    model.eval()
    return model

def is_deepfake_model_ready() -> bool:
    """Check whether a trained deepfake checkpoint exists on disk."""
    from src.deepfake.inference import is_model_trained
    return is_model_trained()
