# ai_detection/api/routes/image.py
"""Image analysis endpoint using EfficientNet model and Grad-CAM generation."""

import os
import uuid
import tempfile
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from ..dependencies import get_image_model
from ..schemas import ImageResponse, ErrorResponse

# Reuse preprocessing and Grad-CAM utilities from src.gradcam
from src.gradcam import load_image, find_target_layer, generate_gradcam, overlay_heatmap, annotate_image

router = APIRouter()

# Maximum image file size: 20 MB
MAX_IMAGE_SIZE_BYTES = 20 * 1024 * 1024

@router.post("/image", response_model=ImageResponse, responses={400: {"model": ErrorResponse}}, summary="Analyze an image and return prediction with Grad-CAM")
async def analyze_image(file: UploadFile = File(...)):
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    # Read and validate file size
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Image file exceeds maximum size of {MAX_IMAGE_SIZE_BYTES // (1024*1024)} MB.",
        )
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Sanitize filename: use UUID to prevent path traversal
    original_ext = Path(file.filename or "image.jpg").suffix or ".jpg"
    safe_stem = uuid.uuid4().hex[:12]
    safe_filename = f"{safe_stem}{original_ext}"

    temp_path = None
    try:
        # Save uploaded file to a temporary location using safe name
        temp_dir = Path(tempfile.gettempdir()) / "truthlens_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = temp_dir / safe_filename
        with open(temp_path, "wb") as f:
            f.write(content)

        # Load image and preprocess
        pil_img, img_tensor = load_image(temp_path)
        device = img_tensor.device
        model = get_image_model().to(device)
        model.eval()

        # Identify target convolutional layer for Grad-CAM
        target_layer = find_target_layer(model)
        activations = []
        gradients = []

        def forward_hook(module, inp, out):
            activations.append(out.detach())

        def backward_hook(module, grad_in, grad_out):
            gradients.append(grad_out[0].detach())

        forward_handle = target_layer.register_forward_hook(forward_hook)
        backward_handle = target_layer.register_backward_hook(backward_hook)

        # Forward pass
        logits = model(img_tensor)
        probs = logits.softmax(dim=1)
        # Class mapping: index 0 = ai_generated, index 1 = real
        ai_prob = float(probs[0, 0].item())
        real_prob = float(probs[0, 1].item())
        # Predicted class is the index with highest probability
        if real_prob > ai_prob:
            pred_class = "real"
            pred_idx = 1
            confidence = real_prob
        else:
            pred_class = "ai_generated"
            pred_idx = 0
            confidence = ai_prob

        # Backward for predicted class
        model.zero_grad()
        loss = probs[0, pred_idx]
        loss.backward()

        activation = activations[0]
        gradient = gradients[0]
        heatmap = generate_gradcam(model, activation, gradient, pred_idx)

        # Clean up hooks
        forward_handle.remove()
        backward_handle.remove()

        # Overlay and annotate
        overlay = overlay_heatmap(pil_img, heatmap)
        annotation = f"Pred: {pred_class} ({confidence:.2%})"
        overlay = annotate_image(overlay, annotation)

        # Save Grad-CAM image to static directory
        # Use original filename stem for the gradcam output so the URL is readable
        original_stem = Path(file.filename or "image").stem
        gradcam_dir = Path(__file__).resolve().parents[3] / "outputs" / "api" / "gradcam"
        os.makedirs(gradcam_dir, exist_ok=True)
        gradcam_path = gradcam_dir / f"gradcam_{original_stem}.png"
        overlay.save(gradcam_path)

        # Return response with relative URL for static serving
        rel_url = f"/static/gradcam/{gradcam_path.name}"
        return ImageResponse(
            predicted_class=str(pred_class),
            ai_probability=float(ai_prob),
            real_probability=float(real_prob),
            confidence=float(confidence),
            gradcam_path=str(rel_url),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary file
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
