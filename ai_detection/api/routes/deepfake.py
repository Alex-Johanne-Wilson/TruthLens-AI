# ai_detection/api/routes/deepfake.py
"""Deepfake video analysis endpoint (prototype — model validation pending)."""

import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..schemas import DeepFakeResponse, ErrorResponse

router = APIRouter()


@router.post(
    "/deepfake",
    response_model=DeepFakeResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Deepfake video analysis (Prototype — Model Validation Pending)",
)
async def deepfake_analysis(file: UploadFile = File(...)):
    """Accept a video file and return a prototype status.

    The deepfake model is untrained; results are not forensically valid.
    """
    # Validate MIME type
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video.")

    suffix = os.path.splitext(file.filename or ".mp4")[1] or ".mp4"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Attempt inference with the prototype (untrained) model
        try:
            from src.deepfake.inference import run_deepfake_inference  # noqa: PLC0415
            run_deepfake_inference(tmp_path, device="cpu")
        except Exception:
            pass  # Inference failure is expected for untrained model

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    return DeepFakeResponse(
        status="prototype",
        message=(
            "Deepfake detection is a prototype. "
            "The model has not been validated and results are not forensically meaningful."
        ),
    )
