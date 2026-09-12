# ai_detection/api/schemas.py
"""Pydantic schemas for request and response models used by the FastAPI backend.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ImageResponse(BaseModel):
    predicted_class: str = Field(..., description="Predicted class label: 'ai_generated' or 'real'")
    ai_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of AI-generated class")
    real_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of real class")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Highest class probability (confidence)")
    gradcam_path: str = Field(..., description="Relative path (URL) to the generated Grad-CAM image")

class DeepFakeResponse(BaseModel):
    status: str = Field(..., description="Status: 'completed', 'model_not_ready', 'insufficient_evidence', 'analysis_failed', 'prototype'")
    overall_prediction: str = Field(..., description="Overall video prediction: 'likely_real', 'likely_fake', 'inconclusive', 'unknown'")
    confidence_score: float = Field(..., description="Confidence score for the overall prediction")
    fake_probability: float = Field(..., description="Average probability of being fake")
    real_probability: float = Field(..., description="Average probability of being real")
    summary: dict = Field(default_factory=dict, description="Summary statistics of processed frames and faces")
    frames: list = Field(default_factory=list, description="List of per-frame analysis results")
    message: str = Field(..., description="Human readable message about the inference result")
    model_ready: bool = Field(default=False, description="Whether a trained deepfake model checkpoint is loaded")
    frames_analyzed: int = Field(default=0, description="Total number of frames sampled from the video")
    faces_detected: int = Field(default=0, description="Total number of faces detected across all frames")
    warnings: List[str] = Field(default_factory=list, description="List of warnings about result reliability")

class DocumentResponse(BaseModel):
    status: str = Field(..., description="Status: 'completed', 'partial', 'failed'")
    file_info: Dict[str, Any] = Field(default_factory=dict, description="File name, size, type, extension")
    document_type: str = Field(default="unknown", description="Detected document type: 'pdf', 'image', 'unknown'")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extracted metadata (EXIF for images, PDF metadata for PDFs)")
    forensic_indicators: List[Dict[str, Any]] = Field(default_factory=list, description="List of forensic findings with severity and description")
    text_extract: Optional[str] = Field(default=None, description="Extracted text content (first ~2000 chars)")
    sha256_hash: Optional[str] = Field(default=None, description="SHA-256 hash of the uploaded file for evidence identification")
    ela_path: Optional[str] = Field(default=None, description="Relative URL to ELA visualization image (images only)")
    warnings: List[str] = Field(default_factory=list, description="Warnings about analysis limitations")
    message: str = Field(default="", description="Human-readable summary of the analysis")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Explanation of the error condition")
