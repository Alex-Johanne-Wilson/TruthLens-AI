"""
tests/test_api_serialization.py

Targeted serialization tests for the TruthLens AI FastAPI backend.
Run from ai_detection directory:
    python -m pytest tests/test_api_serialization.py -v
"""

import io
import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Make sure the src package is importable when running from ai_detection dir
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# ---------------------------------------------------------------------------
# Import FastAPI test client
# ---------------------------------------------------------------------------
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


# ===========================================================================
# 1.  /health
# ===========================================================================
def test_health_returns_200():
    """GET /health must return HTTP 200."""
    resp = client.get("/health")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"


# ===========================================================================
# 2.  sanitize_for_serialization utility
# ===========================================================================
def test_sanitize_numpy_int32():
    from src.utils import sanitize_for_serialization
    v = np.int32(42)
    result = sanitize_for_serialization(v)
    assert isinstance(result, int), f"Expected int, got {type(result)}"
    assert result == 42


def test_sanitize_numpy_float64():
    from src.utils import sanitize_for_serialization
    v = np.float64(0.987654)
    result = sanitize_for_serialization(v)
    assert isinstance(result, float), f"Expected float, got {type(result)}"


def test_sanitize_numpy_bool_():
    from src.utils import sanitize_for_serialization
    v = np.bool_(True)
    result = sanitize_for_serialization(v)
    assert isinstance(result, bool), f"Expected bool, got {type(result)}"


def test_sanitize_numpy_ndarray():
    from src.utils import sanitize_for_serialization
    v = np.array([1, 2, 3], dtype=np.int64)
    result = sanitize_for_serialization(v)
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert all(isinstance(x, int) for x in result)


def test_sanitize_nested_dict():
    from src.utils import sanitize_for_serialization
    v = {
        "a": np.int32(1),
        "b": np.float32(2.5),
        "c": [np.int64(3), np.bool_(False)],
        "d": {"nested": np.ndarray([1])}
    }
    result = sanitize_for_serialization(v)
    # Must be JSON-serializable
    raw = json.dumps(result)
    assert isinstance(raw, str)


def test_sanitize_torch_tensor():
    import torch
    from src.utils import sanitize_for_serialization
    t = torch.tensor([1.0, 2.0, 3.0])
    result = sanitize_for_serialization(t)
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert all(isinstance(x, float) for x in result)


def test_sanitize_scalar_tensor():
    import torch
    from src.utils import sanitize_for_serialization
    t = torch.tensor(42)
    result = sanitize_for_serialization(t)
    assert isinstance(result, int) or isinstance(result, float), f"Expected scalar, got {type(result)}"


# ===========================================================================
# 3.  Deepfake inference data types (unit test on aggregate/infer outputs)
# ===========================================================================
def test_aggregate_video_results_types():
    """aggregate_video_results must return only JSON-serializable types."""
    from src.deepfake.inference import aggregate_video_results

    # Simulate frame_results with Python native types
    frame_results = [
        {"faces": [{"fake_prob": 0.7, "real_prob": 0.3}]},
        {"faces": []},
        {"faces": [{"fake_prob": 0.4, "real_prob": 0.6}]},
    ]
    summary = aggregate_video_results(frame_results)

    # All values in summary must be JSON-serializable
    raw = json.dumps(summary)
    assert isinstance(raw, str)
    # Types check
    assert isinstance(summary["total_sampled_frames"], int)
    assert isinstance(summary["average_fake_prob"], float)
    assert isinstance(summary["video_prediction"], str)


def test_bbox_serializable():
    """bbox returned from detect_faces must be a list of plain Python ints."""
    import cv2
    import numpy as np
    from src.deepfake.face_detection import detect_faces, load_face_detector

    # Create a synthetic blank frame (no real face — we just check the output types)
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    try:
        detector = load_face_detector()
        faces = detect_faces(frame, detector)
    except RuntimeError:
        pytest.skip("Haar cascade not available in test environment")

    for face in faces:
        for coord in face["bbox"]:
            assert isinstance(coord, int), f"bbox coord should be int, got {type(coord)}"


# ===========================================================================
# 4.  POST /api/analyze/deepfake — no PydanticSerializationError
# ===========================================================================
@pytest.mark.skipif(
    not any(
        Path(p).exists()
        for p in [
            "tests/fixtures/sample.mp4",
            "tests/fixtures/sample.mov",
        ]
    ),
    reason="No sample video fixture present — skipping live endpoint test",
)
def test_deepfake_endpoint_no_serialization_error():
    """POST /api/analyze/deepfake must return 200 with a fully JSON-serializable body."""
    # Look for any sample video in fixtures
    for candidate in ["tests/fixtures/sample.mp4", "tests/fixtures/sample.mov"]:
        p = Path(candidate)
        if p.exists():
            video_path = p
            break

    with open(video_path, "rb") as f:
        content = f.read()

    resp = client.post(
        "/api/analyze/deepfake",
        files={"file": (video_path.name, io.BytesIO(content), "video/mp4")},
    )

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    # Ensure it's serializable
    raw = json.dumps(body)
    assert isinstance(raw, str)
    # Check expected keys
    assert "status" in body
    assert "overall_prediction" in body
    assert "confidence_score" in body
    assert isinstance(body["confidence_score"], float)


# ===========================================================================
# 5.  Synthetic deepfake test (creates a tiny video with OpenCV)
# ===========================================================================
def _create_synthetic_video(path: Path, frames: int = 5):
    """Write a minimal synthetic video with cv2 for testing."""
    import cv2
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, 5.0, (64, 64))
    for _ in range(frames):
        frame = np.zeros((64, 64, 3), dtype=np.uint8)
        writer.write(frame)
    writer.release()


def test_deepfake_endpoint_synthetic_video(tmp_path):
    """POST /api/analyze/deepfake with a small synthetic video must return 200
    and a fully JSON-serializable body (no PydanticSerializationError)."""
    video_path = tmp_path / "synthetic.mp4"
    _create_synthetic_video(video_path)

    with open(video_path, "rb") as f:
        content = f.read()

    resp = client.post(
        "/api/analyze/deepfake",
        files={"file": ("synthetic.mp4", io.BytesIO(content), "video/mp4")},
    )

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    body = resp.json()
    # Must be fully JSON-serializable
    raw = json.dumps(body)
    assert isinstance(raw, str)

    # Validate response shape matches schema
    assert "status" in body
    assert "overall_prediction" in body
    assert "confidence_score" in body
    assert "fake_probability" in body
    assert "real_probability" in body
    assert "summary" in body
    assert "frames" in body
    assert "message" in body

    # Type assertions
    assert isinstance(body["confidence_score"], float)
    assert isinstance(body["fake_probability"], float)
    assert isinstance(body["real_probability"], float)
    assert isinstance(body["frames"], list)
    assert isinstance(body["summary"], dict)
