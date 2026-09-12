import cv2
import math
from pathlib import Path

def open_video(video_path: Path):
    """Open video with OpenCV and return VideoCapture object.
    Raises ValueError if video cannot be opened.
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Unable to open video: {video_path}")
    return cap

def get_video_metadata(cap: cv2.VideoCapture):
    """Extract FPS and total frame count (if available)."""
    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    return {"fps": fps, "total_frames": total}

def sample_frames(video_path: Path, max_frames: int = 30, interval_seconds: float = 1.0):
    """Yield sampled frames (as BGR numpy arrays) with their index and timestamp.

    - If the video has FPS info, sample every `interval_seconds`.
    - If FPS is missing or zero, fallback to uniform sampling up to `max_frames`.
    - Does not load all frames into memory at once.
    """
    cap = open_video(video_path)
    meta = get_video_metadata(cap)
    fps = meta["fps"]
    total = meta["total_frames"]
    if fps > 0 and total > 0:
        step = max(1, int(round(fps * interval_seconds)))
        indices = list(range(0, total, step))[:max_frames]
    else:
        # fallback uniform sampling
        indices = list(range(0, max_frames))
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
        timestamp = idx / fps if fps > 0 else None
        frames.append({"index": idx, "timestamp": timestamp, "frame": frame})
    cap.release()
    return frames
