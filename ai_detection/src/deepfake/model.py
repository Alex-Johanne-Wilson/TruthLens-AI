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
        """Expect a batch of BGR OpenCV images (uint8). Convert to RGB inside."""
        # Convert BGR -> RGB and apply preprocessing per image
        if isinstance(x, list):
            tensors = [self.preprocess(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) for img in x]
            x = torch.stack(tensors)
        else:
            # single image
            img = cv2.cvtColor(x, cv2.COLOR_BGR2RGB)
            x = self.preprocess(img).unsqueeze(0)
        return self.backbone(x)

def build_deepfake_model(pretrained: bool = True, device: str = "cpu"):
    """Factory to create the model and move it to the requested device.
    Returns the model ready for inference.
    """
    model = DeepFakeResNet(pretrained=pretrained)
    return model.to(device)
