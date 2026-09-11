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

        # Attempt inference with the trained model
        try:
            from src.deepfake.inference import run_deepfake_inference  # noqa: PLC0415
            from src.utils import sanitize_for_serialization  # noqa: PLC0415
            frame_results, summary = run_deepfake_inference(tmp_path, device="cpu")
            
            clean_summary = sanitize_for_serialization(summary)
            clean_frames = sanitize_for_serialization(frame_results)
            
            overall_pred = str(clean_summary.get("video_prediction", "unknown"))
            avg_fake = float(clean_summary.get("average_fake_prob", 0.0))
            avg_real = float(clean_summary.get("average_real_prob", 0.0))
            conf = avg_fake if overall_pred == "fake" else avg_real

            return DeepFakeResponse(
                status="completed",
                overall_prediction=overall_pred,
                confidence_score=float(conf),
                fake_probability=avg_fake,
                real_probability=avg_real,
                summary=clean_summary,
                frames=clean_frames,
                message="Deepfake detection completed successfully."
            )
        except Exception as e:
            return DeepFakeResponse(
                status="prototype",
                overall_prediction="unknown",
                confidence_score=0.0,
                fake_probability=0.0,
                real_probability=0.0,
                summary={},
                frames=[],
                message=f"Deepfake detection is in prototype or failed: {str(e)}"
            )

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
