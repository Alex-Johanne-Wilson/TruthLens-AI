# ai_detection/api/schemas.py
"""Pydantic schemas for request and response models used by the FastAPI backend.
"""
from pydantic import BaseModel, Field
from typing import Optional

class ImageResponse(BaseModel):
    predicted_class: str = Field(..., description="Predicted class label: 'ai_generated' or 'real'")
    ai_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of AI-generated class")
    real_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of real class")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Highest class probability (confidence)")
    gradcam_path: str = Field(..., description="Relative path (URL) to the generated Grad-CAM image")

class DeepFakeResponse(BaseModel):
    status: str = Field(..., description="Model status – indicates that the model is untrained/unvalidated")
    message: str = Field(..., description="Human readable message about the inference result")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Explanation of the error condition")
