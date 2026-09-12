import json
import torch
from pathlib import Path
from .video import sample_frames
from .face_detection import load_face_detector, detect_faces
from .model import build_deepfake_model

# ------------------------------------------------------------
# Model readiness utilities
# ------------------------------------------------------------

# Path to the trained deepfake checkpoint (relative to project root)
_CHECKPOINT_RELATIVE = Path("outputs") / "checkpoints" / "deepfake_resnet18.pth"


def _get_checkpoint_path() -> Path:
    """Resolve the absolute path to the deepfake model checkpoint."""
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    return base_dir / _CHECKPOINT_RELATIVE


def is_model_trained() -> bool:
    """Check whether a trained deepfake model checkpoint file exists."""
    return _get_checkpoint_path().exists()


# ------------------------------------------------------------
# Inference utilities
# ------------------------------------------------------------

def infer_frame(frame_dict, model, detector, device="cpu"):
    """Run face detection and deepfake classification on a single frame."""
    frame = frame_dict["frame"]
    faces = detect_faces(frame, detector)
    results = []
    for face in faces:
        crop = face["crop"]
        # Validate crop is not empty
        if crop is None or crop.size == 0:
            continue
        # Model expects BGR numpy array (will convert internally)
        with torch.no_grad():
            logits = model(crop)
            probs = torch.softmax(logits, dim=1).squeeze().cpu().numpy()
        fake_prob = float(probs[0].item() if hasattr(probs[0], "item") else probs[0])
        real_prob = float(probs[1].item() if hasattr(probs[1], "item") else probs[1])
        pred_class = int(probs.argmax().item() if hasattr(probs.argmax(), "item") else probs.argmax())
        results.append({
            "bbox": [int(b) for b in face["bbox"]],
            "fake_prob": fake_prob,
            "real_prob": real_prob,
            "pred_class": pred_class,
        })
    out = {
        "frame_index": int(frame_dict["index"]),
        "timestamp": float(frame_dict["timestamp"]) if frame_dict["timestamp"] is not None else 0.0,
        "faces": results,
    }
    return out


def aggregate_video_results(frame_results, fake_threshold=0.5):
    """Aggregate per-frame face predictions into a video-level summary.

    Returns a dict containing counts, averaged probabilities, and an honest
    assessment label (likely_real / likely_fake / inconclusive).
    """
    total_frames = int(len(frame_results))
    frames_with_faces = int(sum(1 for fr in frame_results if fr["faces"]))
    total_faces = int(sum(len(fr["faces"]) for fr in frame_results))

    if total_faces == 0:
        avg_fake = avg_real = 0.0
        fake_percent = 0.0
        video_pred = "inconclusive"
    else:
        fake_probs = [float(f["fake_prob"]) for fr in frame_results for f in fr["faces"]]
        real_probs = [float(f["real_prob"]) for fr in frame_results for f in fr["faces"]]
        avg_fake = float(sum(fake_probs) / total_faces)
        avg_real = float(sum(real_probs) / total_faces)
        fake_percent = float((sum(1 for p in fake_probs if p >= fake_threshold) / total_faces) * 100)

        # Use more nuanced labeling instead of binary fake/real
        if avg_fake >= 0.7:
            video_pred = "likely_fake"
        elif avg_real >= 0.7:
            video_pred = "likely_real"
        else:
            video_pred = "inconclusive"

    summary = {
        "total_sampled_frames": total_frames,
        "frames_with_faces": frames_with_faces,
        "frames_without_faces": int(total_frames - frames_with_faces),
        "total_analyzed_faces": total_faces,
        "average_fake_prob": float(avg_fake),
        "average_real_prob": float(avg_real),
        "percentage_fake_predictions": float(fake_percent),
        "video_prediction": str(video_pred),
    }
    return summary


def run_deepfake_inference(video_path: str, max_frames: int = 30, interval_seconds: float = 1.0, device: str = "cpu"):
    """Full pipeline: load video, sample frames, detect faces, classify, aggregate.

    Returns a tuple (frame_results, summary, model_trained_flag).
    The third element indicates whether a real trained checkpoint was loaded.
    """
    from ..utils import sanitize_for_serialization

    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Check model readiness BEFORE processing
    checkpoint_path = _get_checkpoint_path()
    model_trained = checkpoint_path.exists()

    # Sample frames
    frames = sample_frames(video_path, max_frames=max_frames, interval_seconds=interval_seconds)

    if len(frames) == 0:
        # No frames could be extracted
        empty_summary = {
            "total_sampled_frames": 0,
            "frames_with_faces": 0,
            "frames_without_faces": 0,
            "total_analyzed_faces": 0,
            "average_fake_prob": 0.0,
            "average_real_prob": 0.0,
            "percentage_fake_predictions": 0.0,
            "video_prediction": "inconclusive",
        }
        return [], empty_summary, model_trained

    # Load model and face detector
    detector = load_face_detector()
    model = build_deepfake_model(pretrained=False, device=device)

    # Load checkpoint if available
    if model_trained:
        model.load_state_dict(torch.load(str(checkpoint_path), map_location=device))
        print(f"Loaded trained deepfake model from {checkpoint_path}")
    else:
        print("Warning: Trained deepfake model not found. Using untrained placeholder.")

    model.eval()

    # Process each frame
    frame_results = []
    for f in frames:
        res = infer_frame(f, model, detector, device=device)
        frame_results.append(res)

    summary = aggregate_video_results(frame_results)

    # If model is untrained, override prediction to inconclusive
    if not model_trained:
        summary["video_prediction"] = "inconclusive"

    # Final safety sanitize across returned dicts
    return (
        sanitize_for_serialization(frame_results),
        sanitize_for_serialization(summary),
        model_trained,
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Deepfake video inference")
    parser.add_argument("--video", type=str, required=True, help="Path to input video file")
    parser.add_argument("--output", type=str, default="deepfake_result.json", help="Where to write JSON result")
    args = parser.parse_args()
    frame_res, summary, trained = run_deepfake_inference(args.video)
    result = {"frames": frame_res, "summary": summary, "model_trained": trained}
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Deepfake analysis saved to {args.output}")
    if not trained:
        print("WARNING: Results are from an UNTRAINED model and are NOT reliable.")
