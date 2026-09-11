"""
EfficientNet-B0 model architecture for AI-generated vs. Real image detection.
Supports ImageNet pretraining, configurable classes, and modular verification.
"""

from typing import Dict, Optional, Tuple

import torch
import torch.nn as nn
from torchvision import models
from torchvision.models import EfficientNet_B0_Weights


# Default architecture constants
DEFAULT_NUM_CLASSES: int = 2
DEFAULT_DROPOUT_RATE: float = 0.2
INPUT_IMAGE_CHANNELS: int = 3
INPUT_IMAGE_SIZE: int = 224

# Consistent class mapping
CLASS_TO_IDX: Dict[str, int] = {
    "ai_generated": 0,
    "real": 1
}
IDX_TO_CLASS: Dict[int, str] = {v: k for k, v in CLASS_TO_IDX.items()}


class EfficientNetB0Detector(nn.Module):
    """
    EfficientNet-B0 backbone adapted for binary (or multi-class) forensic detection.
    
    The classification head is replaced to output `num_classes` logits (default: 2),
    with dropout matching the original EfficientNet architecture.
    Backbone parameters remain unfrozen by default; freezing / fine-tuning strategy
    is managed separately during the training stage.
    """

    def __init__(
        self,
        num_classes: int = DEFAULT_NUM_CLASSES,
        pretrained: bool = True,
        dropout_rate: float = DEFAULT_DROPOUT_RATE
    ) -> None:
        super().__init__()
        self.num_classes = num_classes
        self.pretrained = pretrained
        self.dropout_rate = dropout_rate

        weights = EfficientNet_B0_Weights.DEFAULT if pretrained else None
        self.backbone = models.efficientnet_b0(weights=weights)

        # Original classifier is Sequential(Dropout(p=0.2), Linear(in_features=1280, out_features=1000))
        in_features = self.backbone.classifier[1].in_features  # 1280

        # Replace classification head to output desired num_classes
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate, inplace=True),
            nn.Linear(in_features=in_features, out_features=num_classes, bias=True)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor of shape (batch_size, 3, 224, 224).
            
        Returns:
            Logits tensor of shape (batch_size, num_classes).
        """
        return self.backbone(x)

    def get_features(self, x: torch.Tensor) -> torch.Tensor:
        """
        Extract penultimate convolutional feature map (useful for Grad-CAM / feature analysis).
        
        Args:
            x: Input tensor of shape (batch_size, 3, 224, 224).
            
        Returns:
            Feature tensor of shape (batch_size, 1280, 7, 7).
        """
        return self.backbone.features(x)


def build_model(
    num_classes: int = DEFAULT_NUM_CLASSES,
    pretrained: bool = True,
    dropout_rate: float = DEFAULT_DROPOUT_RATE,
    device: Optional[torch.device] = None
) -> EfficientNetB0Detector:
    """
    Factory function to instantiate the EfficientNet-B0 detector.

    Args:
        num_classes: Number of output classes (default: 2).
        pretrained: Whether to load weights pretrained on ImageNet-1k (default: True).
        dropout_rate: Dropout probability in the classifier head (default: 0.2).
        device: Target torch device (CPU or CUDA). Defaults to auto-detection.

    Returns:
        Instantiated EfficientNetB0Detector module on target device.
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = EfficientNetB0Detector(
        num_classes=num_classes,
        pretrained=pretrained,
        dropout_rate=dropout_rate
    )
    return model.to(device)


def get_model_summary(model: nn.Module) -> Dict:
    """
    Computes parameter metrics and architectural details for the model.
    """
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    non_trainable_params = total_params - trainable_params

    num_classes = getattr(model, "num_classes", DEFAULT_NUM_CLASSES)

    return {
        "architecture": "EfficientNet-B0",
        "num_classes": num_classes,
        "class_mapping": CLASS_TO_IDX,
        "total_parameters": total_params,
        "trainable_parameters": trainable_params,
        "non_trainable_parameters": non_trainable_params,
        "expected_input_shape": (INPUT_IMAGE_CHANNELS, INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE),
        "output_shape": (num_classes,)
    }


def verify_model(data_dir: Optional[str] = None) -> Dict:
    """
    Verifies model architecture and execution integrity:
      1. Instantiates model with default ImageNet pretraining.
      2. Validates dummy tensor forward pass: [2, 3, 224, 224] -> [2, 2].
      3. Verifies finite output values and eval mode behavior.
      4. If data_dir is provided, performs a real forward pass with one actual DataLoader batch.
      5. Runs device checks (CPU and CUDA if available).

    Returns:
        Dictionary containing all verification diagnostics.
    """
    devices_to_test = [torch.device("cpu")]
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        devices_to_test.append(torch.device("cuda:0"))

    verification_results = {
        "cuda_available": cuda_available,
        "devices_tested": [str(d) for d in devices_to_test],
        "device_checks": {}
    }

    # Use CPU for baseline summary
    cpu_model = build_model(device=torch.device("cpu"))
    cpu_model.eval()
    summary = get_model_summary(cpu_model)
    verification_results["model_summary"] = summary

    # 1. Dummy tensor verification on all supported devices
    dummy_input_shape = (2, 3, 224, 224)
    expected_dummy_output_shape = (2, 2)

    for dev in devices_to_test:
        dev_name = str(dev)
        m = build_model(device=dev)
        m.eval()

        dummy_x = torch.randn(dummy_input_shape, device=dev)
        with torch.no_grad():
            dummy_out = m(dummy_x)

        assert dummy_out.shape == expected_dummy_output_shape, (
            f"Shape mismatch on {dev_name}: expected {expected_dummy_output_shape}, got {dummy_out.shape}"
        )
        assert torch.isfinite(dummy_out).all(), f"Non-finite values encountered on {dev_name}"

        verification_results["device_checks"][dev_name] = {
            "dummy_input_shape": list(dummy_input_shape),
            "dummy_output_shape": list(dummy_out.shape),
            "output_finite": bool(torch.isfinite(dummy_out).all()),
            "status": "passed"
        }

    # 2. Real DataLoader batch forward pass if data_dir is specified
    if data_dir is not None:
        from pathlib import Path
        # Import get_dataloaders from dataset.py
        try:
            from src.dataset import get_dataloaders
        except ImportError:
            from dataset import get_dataloaders

        train_loader, _, _ = get_dataloaders(data_dir=Path(data_dir), batch_size=16)
        real_images, real_labels = next(iter(train_loader))

        cpu_model.eval()
        with torch.no_grad():
            real_out = cpu_model(real_images)

        assert real_out.shape == (real_images.shape[0], 2), (
            f"Expected real output shape ({real_images.shape[0]}, 2), got {real_out.shape}"
        )
        assert torch.isfinite(real_out).all(), "Non-finite output values detected in real batch forward pass"

        verification_results["real_batch_check"] = {
            "batch_size": int(real_images.shape[0]),
            "real_input_shape": list(real_images.shape),
            "real_output_shape": list(real_out.shape),
            "labels_shape": list(real_labels.shape),
            "all_outputs_finite": bool(torch.isfinite(real_out).all()),
            "status": "passed"
        }

    return verification_results


if __name__ == "__main__":
    from pathlib import Path
    base_data = Path(__file__).resolve().parent.parent / "data"
    print("Running EfficientNet-B0 model verification...")
    results = verify_model(data_dir=str(base_data))
    import pprint
    pprint.pprint(results)
