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
    """Run face detection and deepfake classification on a single frame.

    Parameters
    ----------
    frame_dict: dict with keys "index", "timestamp", "frame" (BGR ndarray)
    model: torch.nn.Module ready for inference
    detector: OpenCV cascade classifier
    device: torch device string

    Returns
    -------
    dict with original frame info plus a list of face predictions.
    Each face prediction contains:
        - bbox (x1, y1, x2, y2)
        - fake_prob, real_prob
        - pred_class (0=fake, 1=real)
    """
    frame = frame_dict["frame"]
    faces = detect_faces(frame, detector)
    results = []
    for face in faces:
        crop = face["crop"]
        # Model expects BGR numpy array (will convert internally)
        with torch.no_grad():
            logits = model(crop)
            probs = torch.softmax(logits, dim=1).squeeze().cpu().numpy()
        fake_prob, real_prob = float(probs[0]), float(probs[1])
        pred_class = int(probs.argmax())
        results.append({
            "bbox": face["bbox"],
            "fake_prob": fake_prob,
            "real_prob": real_prob,
            "pred_class": pred_class,
        })
    out = {
        "frame_index": frame_dict["index"],
        "timestamp": frame_dict["timestamp"],
        "faces": results,
    }
    return out

def aggregate_video_results(frame_results, fake_threshold=0.5):
    """Aggregate per‑frame face predictions into a video‑level summary.

    Returns a dict containing counts and averaged probabilities.
    """
    total_frames = len(frame_results)
    frames_with_faces = sum(1 for fr in frame_results if fr["faces"])
    total_faces = sum(len(fr["faces"]) for fr in frame_results)
    if total_faces == 0:
        avg_fake = avg_real = 0.0
        fake_percent = 0.0
    else:
        fake_probs = [f["fake_prob"] for fr in frame_results for f in fr["faces"]]
        real_probs = [f["real_prob"] for fr in frame_results for f in fr["faces"]]
        avg_fake = sum(fake_probs) / total_faces
        avg_real = sum(real_probs) / total_faces
        fake_percent = (sum(1 for p in fake_probs if p >= fake_threshold) / total_faces) * 100
    video_pred = "fake" if avg_fake >= fake_threshold else "real"
    summary = {
        "total_sampled_frames": total_frames,
        "frames_with_faces": frames_with_faces,
        "frames_without_faces": total_frames - frames_with_faces,
        "total_analyzed_faces": total_faces,
        "average_fake_prob": avg_fake,
        "average_real_prob": avg_real,
        "percentage_fake_predictions": fake_percent,
        "video_prediction": video_pred,
    }
    return summary

def run_deepfake_inference(video_path: str, max_frames: int = 30, interval_seconds: float = 1.0, device: str = "cpu"):
    """Full pipeline: load video, sample frames, detect faces, classify, aggregate.
    Returns a tuple (frame_results, summary).
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    # Sample frames
    frames = sample_frames(video_path, max_frames=max_frames, interval_seconds=interval_seconds)
    # Load model (untrained placeholder) and face detector
    detector = load_face_detector()
    model = build_deepfake_model(pretrained=False, device=device)
    model.eval()
    # Process each frame
    frame_results = []
    for f in frames:
        res = infer_frame(f, model, detector, device=device)
        frame_results.append(res)
    summary = aggregate_video_results(frame_results)
    return frame_results, summary

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
