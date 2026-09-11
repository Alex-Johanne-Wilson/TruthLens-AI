import os
from pathlib import Path
from PIL import Image
import torch
from torch.utils.data import Dataset
from torchvision import transforms

class DeepfakeDataset(Dataset):
    """
    Dataset for loading deepfake vs real face images.
    Label mapping:
    0 = fake
    1 = real
    """
    def __init__(self, root_dir: str, split: str = "train", transform=None):
        """
        root_dir: path to ai_detection/data/deepfake
        split: "train", "val", or "test"
        """
        self.root_dir = Path(root_dir) / split
        self.split = split
        self.samples = []
        self.transform = transform
        
        # Default transforms if none provided
        if self.transform is None:
            if split == "train":
                self.transform = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.RandomHorizontalFlip(),
                    transforms.RandomRotation(10),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                         std=[0.229, 0.224, 0.225]),
                ])
            else:
                self.transform = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                         std=[0.229, 0.224, 0.225]),
                ])

        # Load samples
        fake_dir = self.root_dir / "fake"
        real_dir = self.root_dir / "real"

        if fake_dir.exists():
            for f in os.listdir(fake_dir):
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    self.samples.append((str(fake_dir / f), 0))
                    
        if real_dir.exists():
            for f in os.listdir(real_dir):
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    self.samples.append((str(real_dir / f), 1))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert("RGB")
        
        if self.transform:
            image = self.transform(image)
            
        return image, torch.tensor(label, dtype=torch.long)
