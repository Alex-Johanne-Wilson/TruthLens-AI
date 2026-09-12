# ai_detection/api/routes/deepfake.py
"""Deepfake video analysis endpoint with honest model readiness reporting."""

import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..schemas import DeepFakeResponse, ErrorResponse

router = APIRouter()

# Maximum video file size: 100 MB
MAX_VIDEO_SIZE_BYTES = 100 * 1024 * 1024


@router.post(
    "/deepfake",
    response_model=DeepFakeResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Deepfake video analysis",
)
async def deepfake_analysis(file: UploadFile = File(...)):
    """Accept a video file and return deepfake detection results.

    If the deepfake model checkpoint is not available, the endpoint returns
    status='model_not_ready' with an honest explanation instead of fabricating
    predictions from untrained weights.
    """
    # ── Validate MIME type ──────────────────────────────────────────
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video (video/* MIME type).")

    # ── Read file and check size ────────────────────────────────────
    content = await file.read()
    if len(content) > MAX_VIDEO_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Video file exceeds maximum size of {MAX_VIDEO_SIZE_BYTES // (1024*1024)} MB.",
        )
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    suffix = os.path.splitext(file.filename or ".mp4")[1] or ".mp4"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        # ── Check model readiness FIRST ─────────────────────────────
        from src.deepfake.inference import is_model_trained  # noqa: PLC0415

        model_trained = is_model_trained()

        if not model_trained:
            # Still attempt inference to gather frame/face statistics,
            # but clearly mark results as unreliable
            try:
                from src.deepfake.inference import run_deepfake_inference  # noqa: PLC0415
                from src.utils import sanitize_for_serialization  # noqa: PLC0415

                frame_results, summary, _ = run_deepfake_inference(tmp_path, device="cpu")
                clean_summary = sanitize_for_serialization(summary)
                clean_frames = sanitize_for_serialization(frame_results)

                total_frames = int(clean_summary.get("total_sampled_frames", 0))
                total_faces = int(clean_summary.get("total_analyzed_faces", 0))
            except Exception:
                clean_summary = {}
                clean_frames = []
                total_frames = 0
                total_faces = 0

            return DeepFakeResponse(
                status="model_not_ready",
                overall_prediction="unknown",
                confidence_score=0.0,
                fake_probability=0.0,
                real_probability=0.0,
                summary=clean_summary,
                frames=clean_frames,
                message=(
                    "The deepfake detection model has not been trained yet. "
                    "No trained checkpoint (deepfake_resnet18.pth) was found. "
                    "The displayed predictions are NOT reliable — they come from "
                    "untrained model weights. A real deepfake dataset and training "
                    "run are required before results can be trusted."
                ),
                model_ready=False,
                frames_analyzed=total_frames,
                faces_detected=total_faces,
                warnings=[
                    "No trained model checkpoint found — results are unreliable.",
                    "Predictions are from an untrained ResNet-18 with random classification head weights.",
                    "Do not use these results for any forensic determination.",
                ],
            )

        # ── Model IS trained — run real inference ───────────────────
        try:
            from src.deepfake.inference import run_deepfake_inference  # noqa: PLC0415
            from src.utils import sanitize_for_serialization  # noqa: PLC0415

            frame_results, summary, trained_flag = run_deepfake_inference(tmp_path, device="cpu")

            clean_summary = sanitize_for_serialization(summary)
            clean_frames = sanitize_for_serialization(frame_results)

            overall_pred = str(clean_summary.get("video_prediction", "inconclusive"))
            avg_fake = float(clean_summary.get("average_fake_prob", 0.0))
            avg_real = float(clean_summary.get("average_real_prob", 0.0))
            total_frames = int(clean_summary.get("total_sampled_frames", 0))
            total_faces = int(clean_summary.get("total_analyzed_faces", 0))

            # Confidence is the probability of the predicted class
            if overall_pred == "likely_fake":
                conf = avg_fake
            elif overall_pred == "likely_real":
                conf = avg_real
            else:
                conf = max(avg_fake, avg_real)

            warnings = []
            if total_faces == 0:
                warnings.append("No faces were detected in any sampled frame — result is inconclusive.")
                overall_pred = "inconclusive"
            if total_faces < 3:
                warnings.append(f"Only {total_faces} face(s) detected — low evidence for a reliable prediction.")

            # Always add forensic disclaimer
            warnings.append(
                "This is an AI-based assessment and does not constitute absolute proof. "
                "Results should be corroborated with additional forensic evidence."
            )

            return DeepFakeResponse(
                status="completed",
                overall_prediction=overall_pred,
                confidence_score=float(conf),
                fake_probability=avg_fake,
                real_probability=avg_real,
                summary=clean_summary,
                frames=clean_frames,
                message="Deepfake detection completed successfully.",
                model_ready=True,
                frames_analyzed=total_frames,
                faces_detected=total_faces,
                warnings=warnings,
            )
        except Exception as e:
            return DeepFakeResponse(
                status="analysis_failed",
                overall_prediction="unknown",
                confidence_score=0.0,
                fake_probability=0.0,
                real_probability=0.0,
                summary={},
                frames=[],
                message=f"Analysis failed: {str(e)}",
                model_ready=model_trained,
                frames_analyzed=0,
                faces_detected=0,
                warnings=["An error occurred during video analysis."],
            )

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
