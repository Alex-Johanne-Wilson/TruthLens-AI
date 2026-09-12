# """
# Grad-CAM implementation for the trained EfficientNet-B0 detector.
# Generates heatmap overlays for a given image (or batch) and saves visualizations.
#
# Usage:
#   python src/gradcam.py --image <path> [--output <dir>] [--checkpoint <path>] [--target-class <int>]
#
# Defaults:
#   --output      -> outputs/gradcam
#   --checkpoint  -> outputs/checkpoints/best_model.pth
#   --target-class: if omitted, uses the model's predicted class.
# """

import argparse
import json
import os
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

# Import model building utilities from the existing codebase
try:
    from src.model import build_model, CLASS_TO_IDX, IDX_TO_CLASS
except ImportError:
    from model import build_model, CLASS_TO_IDX, IDX_TO_CLASS

# ImageNet normalization (must match training pipeline)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def load_image(image_path: Path) -> Tuple[Image.Image, torch.Tensor]:
    """Load an image, keep the original PIL image and return a pre‑processed tensor.
    The tensor is normalized exactly as during training (224×224).
    """
    pil_img = Image.open(image_path).convert("RGB")
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])
    tensor = preprocess(pil_img).unsqueeze(0)  # shape (1, 3, 224, 224)
    return pil_img, tensor

def find_target_layer(model: torch.nn.Module) -> torch.nn.Module:
    """Identify the final convolutional feature map layer.
    For EfficientNet‑B0 the appropriate layer is the last Conv2dNormActivation
    block (named ``features[8]``) which outputs a (B, 1280, 7, 7) tensor.
    """
    # ``model.backbone.features`` is a ``torch.nn.Sequential`` of 9 blocks.
    # The last block (index 8) is a Conv2dNormActivation.
    target = model.backbone.features[8]
    return target

def generate_gradcam(
    model: torch.nn.Module,
    activation: torch.Tensor,
    gradients: torch.Tensor,
    target_class: int,
) -> np.ndarray:
    """Compute Grad‑CAM heatmap.
    Returns a ``numpy`` array of shape (H, W) with values in [0, 1].
    """
    # gradients: (B, C, H, W)
    # activation: (B, C, H, W)
    # Global‑average‑pool the gradients over spatial dimensions
    weights = torch.mean(gradients, dim=(2, 3), keepdim=True)  # (B, C, 1, 1)
    # Weighted combination of forward activations
    cam = torch.sum(weights * activation, dim=1, keepdim=True)  # (B, 1, H, W)
    cam = F.relu(cam)  # keep only positive influence
    cam = cam.squeeze().cpu().numpy()  # (H, W)
    # Normalize to [0, 1]
    cam -= cam.min()
    if cam.max() > 0:
        cam /= cam.max()
    return cam

def overlay_heatmap(pil_img: Image.Image, heatmap: np.ndarray) -> Image.Image:
    """Resize heatmap to original image size and overlay on the image.
    Returns a PIL image with the heatmap blended (alpha=0.4).
    """
    # Convert PIL image to OpenCV format (BGR) for blending
    img_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    # Resize heatmap to image size
    heatmap_resized = cv2.resize(heatmap, (img_cv.shape[1], img_cv.shape[0]))
    # Convert heatmap to 0‑255 uint8 colormap
    heatmap_uint8 = np.uint8(255 * heatmap_resized)
    heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    # Blend heatmap with original image
    overlay = cv2.addWeighted(img_cv, 0.6, heatmap_color, 0.4, 0)
    # Back to RGB PIL image
    overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
    return Image.fromarray(overlay_rgb)

def annotate_image(pil_img: Image.Image, text: str) -> Image.Image:
    """Draw a simple text annotation at the top‑left corner.
    Uses Pillow's built‑in drawing; requires a font that exists on the system.
    """
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(pil_img)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except Exception:
        font = ImageFont.load_default()
    # Semi‑transparent rectangle for readability
    rect_fill = (0, 0, 0, 128)
    draw.rectangle([0, 0, pil_img.width, 20], fill=rect_fill)
    draw.text((5, 2), text, fill=(255, 255, 255), font=font)
    return pil_img

# ------------------------------------------------------------
# Main execution
# ------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Grad‑CAM for TruthLens AI detector")
    parser.add_argument("--image", type=str, required=True, help="Path to input image")
    parser.add_argument("--output", type=str, default="outputs/gradcam", help="Directory to store visualizations")
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="outputs/checkpoints/best_model.pth",
        help="Path to trained EfficientNet‑B0 checkpoint",
    )
    parser.add_argument(
        "--target-class",
        type=int,
        default=None,
        help="Explicit target class index (0 = ai_generated, 1 = real). If omitted, uses model prediction.",
    )
    args = parser.parse_args()

    image_path = Path(args.image)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(num_classes=2, pretrained=False, device=device)
    checkpoint = torch.load(args.checkpoint, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    # Identify target convolutional layer
    target_layer = find_target_layer(model)
    # Containers for activations / gradients
    activations = []
    gradients = []

    def forward_hook(module, inp, out):
        activations.append(out.detach())

    def backward_hook(module, grad_in, grad_out):
        gradients.append(grad_out[0].detach())

    # Register hooks
    forward_handle = target_layer.register_forward_hook(forward_hook)
    backward_handle = target_layer.register_backward_hook(backward_hook)

    # Load and preprocess image
    orig_pil, img_tensor = load_image(image_path)
    img_tensor = img_tensor.to(device)

    # Forward pass
    logits = model(img_tensor)
    probs = torch.softmax(logits, dim=1)
    pred_idx = torch.argmax(probs, dim=1).item()
    target_idx = args.target_class if args.target_class is not None else pred_idx

    # Backward pass for the target class
    model.zero_grad()
    loss = probs[0, target_idx]
    loss.backward()

    # Grab stored activations / gradients (batch size = 1)
    activation = activations[0]
    gradient = gradients[0]

    # Compute Grad‑CAM heatmap
    heatmap = generate_gradcam(model, activation, gradient, target_idx)

    # Create overlay
    overlay = overlay_heatmap(orig_pil, heatmap)

    # Annotate image with prediction details
    pred_class = IDX_TO_CLASS[pred_idx]
    target_class = IDX_TO_CLASS[target_idx]
    confidence = probs[0, pred_idx].item()
    annotation = f"Pred: {pred_class} ({confidence:.2%}) | Target: {target_class}"
    overlay = annotate_image(overlay, annotation)

    # Save overlay
    out_path = output_dir / f"gradcam_{image_path.stem}.png"
    overlay.save(out_path)
    print(f"Grad-CAM visualization saved to: {out_path}")
    # Clean up hooks
    forward_handle.remove()
    backward_handle.remove()


if __name__ == "__main__":
    main()
