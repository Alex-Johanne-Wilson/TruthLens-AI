import cv2
from pathlib import Path

def load_face_detector():
    """Load Haar cascade face detector from OpenCV data.
    Returns the cascade classifier.
    """
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    if detector.empty():
        raise RuntimeError("Failed to load Haar cascade for face detection.")
    return detector

def detect_faces(frame: "numpy.ndarray", detector, padding: float = 0.2):
    """Detect faces in a BGR frame.
    Returns list of dicts with bounding box and cropped face (BGR array).
    Padding is fraction of bbox size added around the face.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    results = []
    h, w = frame.shape[:2]
    for (x, y, fw, fh) in faces:
        # Apply padding
        pad_w = int(fw * padding)
        pad_h = int(fh * padding)
        x1 = max(x - pad_w, 0)
        y1 = max(y - pad_h, 0)
        x2 = min(x + fw + pad_w, w)
        y2 = min(y + fh + pad_h, h)
        crop = frame[y1:y2, x1:x2]
        results.append({
            "bbox": (x1, y1, x2, y2),
            "crop": crop,
        })
    return results
