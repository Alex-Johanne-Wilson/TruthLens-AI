import json
import torch
from pathlib import Path
from .video import sample_frames
from .face_detection import load_face_detector, detect_faces
from .model import build_deepfake_model

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
        "timestamp": float(frame_dict["timestamp"]),
        "faces": results,
    }
    return out

def aggregate_video_results(frame_results, fake_threshold=0.5):
    """Aggregate per‑frame face predictions into a video‑level summary.

    Returns a dict containing counts and averaged probabilities.
    """
    total_frames = int(len(frame_results))
    frames_with_faces = int(sum(1 for fr in frame_results if fr["faces"]))
    total_faces = int(sum(len(fr["faces"]) for fr in frame_results))
    if total_faces == 0:
        avg_fake = avg_real = 0.0
        fake_percent = 0.0
    else:
        fake_probs = [float(f["fake_prob"]) for fr in frame_results for f in fr["faces"]]
        real_probs = [float(f["real_prob"]) for fr in frame_results for f in fr["faces"]]
        avg_fake = float(sum(fake_probs) / total_faces)
        avg_real = float(sum(real_probs) / total_faces)
        fake_percent = float((sum(1 for p in fake_probs if p >= fake_threshold) / total_faces) * 100)
    video_pred = "fake" if avg_fake >= fake_threshold else "real"
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
    Returns a tuple (frame_results, summary).
    """
    from ..utils import sanitize_for_serialization

    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    # Sample frames
    frames = sample_frames(video_path, max_frames=max_frames, interval_seconds=interval_seconds)
    # Load model (untrained placeholder) and face detector
    detector = load_face_detector()
    model = build_deepfake_model(pretrained=False, device=device)
    
    # Load checkpoint if available
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    checkpoint_path = base_dir / "outputs" / "checkpoints" / "deepfake_resnet18.pth"
    if checkpoint_path.exists():
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
    
    # Final safety sanitize across returned dicts
    return sanitize_for_serialization(frame_results), sanitize_for_serialization(summary)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Deepfake video inference (placeholder model)")
    parser.add_argument("--video", type=str, required=True, help="Path to input video file")
    parser.add_argument("--output", type=str, default="deepfake_result.json", help="Where to write JSON result")
    args = parser.parse_args()
    frame_res, summary = run_deepfake_inference(args.video)
    result = {"frames": frame_res, "summary": summary}
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Deepfake analysis saved to {args.output}")
