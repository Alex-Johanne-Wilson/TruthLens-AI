# ai_detection/api/dependencies.py
"""Dependency utilities for FastAPI.
Loads the EfficientNet image model and the deepfake model (untrained).
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

# Deepfake model loading (placeholder – untrained)
@lru_cache()
def get_deepfake_model():
    # Import deepfake inference utilities; the model is untrained/validation pending.
    from src.deepfake.model import build_deepfake_model
    model = build_deepfake_model(pretrained=False)
    # No checkpoint loading – model remains untrained.
    model.eval()
    return model
