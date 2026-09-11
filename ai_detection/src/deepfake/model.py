import cv2
import torch
import torch.nn as nn
import torchvision.models as models
from torchvision import transforms

# Simple deepfake classifier based on pretrained ResNet18 backbone (CPU-friendly)
# Output: 2 logits (0 = fake, 1 = real)

class DeepFakeResNet(nn.Module):
    def __init__(self, pretrained: bool = True, num_classes: int = 2):
        super().__init__()
        self.backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT if pretrained else None)
        # Replace final fully‑connected layer
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(in_features, num_classes)
        self.preprocess = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])

    def forward(self, x):
        """Expect a batch of BGR OpenCV images (uint8), a single image, or a pre-processed tensor batch."""
        if isinstance(x, torch.Tensor) and x.ndim == 4:
            # If x is already a batch tensor (e.g. from DataLoader), pass straight to backbone
            return self.backbone(x)
        
        # Otherwise, assume OpenCV BGR arrays and apply preprocessing
        if isinstance(x, list):
            tensors = [self.preprocess(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) for img in x]
            x = torch.stack(tensors)
        else:
            # single image
            img = cv2.cvtColor(x, cv2.COLOR_BGR2RGB)
            x = self.preprocess(img).unsqueeze(0)
            
        # Ensure tensor is on the correct device (the same as the model)
        device = next(self.backbone.parameters()).device
        x = x.to(device)
            
        return self.backbone(x)

def build_deepfake_model(pretrained: bool = True, device: str = "cpu"):
    """Factory to create the model and move it to the requested device.
    Returns the model ready for inference.
    """
    model = DeepFakeResNet(pretrained=pretrained)
    return model.to(device)
