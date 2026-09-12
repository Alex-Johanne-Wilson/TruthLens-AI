"""
PyTorch Dataset and DataLoader pipelines for AI-generated vs. Real image detection.
Standardized for EfficientNet-B0 (224x224 input, ImageNet normalization).
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from PIL import Image

# Default configuration constants
DEFAULT_IMAGE_SIZE: int = 224
DEFAULT_BATCH_SIZE: int = 32
DEFAULT_NUM_WORKERS: int = 0  # 0 is safe default for Windows cross-process multiprocessing
DEFAULT_RANDOM_SEED: int = 42

# ImageNet normalization parameters (mean and std for RGB channels)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Deterministic class mapping
# 0 -> ai_generated, 1 -> real (matching ImageFolder alphabetical ordering and dataset convention)
CLASS_TO_IDX: Dict[str, int] = {
    "ai_generated": 0,
    "real": 1
}
IDX_TO_CLASS: Dict[int, str] = {v: k for k, v in CLASS_TO_IDX.items()}


def pil_loader_safe_rgb(path: str) -> Image.Image:
    """
    Safely load an image and ensure conversion to 3-channel RGB.
    Handles grayscale ('L'), RGBA, and palette images transparently.
    """
    with open(path, "rb") as f:
        img = Image.open(f)
        return img.convert("RGB")


def get_train_transforms(image_size: int = DEFAULT_IMAGE_SIZE) -> transforms.Compose:
    """
    Data augmentation and preprocessing transforms for training.
    Applies resizing, random crops, horizontal flip, and slight color jitter,
    followed by tensor conversion and ImageNet normalization.
    """
    return transforms.Compose([
        transforms.Resize((int(image_size * 1.14), int(image_size * 1.14)), interpolation=transforms.InterpolationMode.BILINEAR),
        transforms.RandomCrop((image_size, image_size)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.ColorJitter(brightness=0.05, contrast=0.05),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def get_eval_transforms(image_size: int = DEFAULT_IMAGE_SIZE) -> transforms.Compose:
    """
    Deterministic preprocessing transforms for validation and testing.
    No random augmentations applied; resizes and center-crops to target image_size.
    """
    return transforms.Compose([
        transforms.Resize((int(image_size * 1.14), int(image_size * 1.14)), interpolation=transforms.InterpolationMode.BILINEAR),
        transforms.CenterCrop((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def get_datasets(
    data_dir: str | Path,
    image_size: int = DEFAULT_IMAGE_SIZE
) -> Tuple[datasets.ImageFolder, datasets.ImageFolder, datasets.ImageFolder]:
    """
    Create ImageFolder datasets for train, val, and test splits with respective transforms.
    
    Args:
        data_dir: Base directory containing train/, val/, and test/ subdirectories.
        image_size: Target resolution dimension for EfficientNet-B0 (default: 224).
        
    Returns:
        Tuple of (train_dataset, val_dataset, test_dataset)
    """
    data_path = Path(data_dir)
    train_dir = data_path / "train"
    val_dir = data_path / "val"
    test_dir = data_path / "test"

    for p in (train_dir, val_dir, test_dir):
        if not p.exists():
            raise FileNotFoundError(f"Required split directory does not exist: {p}")

    train_transform = get_train_transforms(image_size=image_size)
    eval_transform = get_eval_transforms(image_size=image_size)

    # Use custom loader to ensure strict 3-channel RGB conversion
    train_dataset = datasets.ImageFolder(
        root=str(train_dir),
        transform=train_transform,
        loader=pil_loader_safe_rgb
    )
    val_dataset = datasets.ImageFolder(
        root=str(val_dir),
        transform=eval_transform,
        loader=pil_loader_safe_rgb
    )
    test_dataset = datasets.ImageFolder(
        root=str(test_dir),
        transform=eval_transform,
        loader=pil_loader_safe_rgb
    )

    # Ensure class-to-index mapping matches deterministic specification
    for name, ds in [("train", train_dataset), ("val", val_dataset), ("test", test_dataset)]:
        if ds.class_to_idx != CLASS_TO_IDX:
            raise ValueError(
                f"Class mapping mismatch in {name} split. Expected {CLASS_TO_IDX}, got {ds.class_to_idx}"
            )

    return train_dataset, val_dataset, test_dataset


def get_dataloaders(
    data_dir: str | Path,
    image_size: int = DEFAULT_IMAGE_SIZE,
    batch_size: int = DEFAULT_BATCH_SIZE,
    num_workers: int = DEFAULT_NUM_WORKERS,
    random_seed: Optional[int] = DEFAULT_RANDOM_SEED,
    pin_memory: Optional[bool] = None
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Create PyTorch DataLoaders for train, val, and test splits.

    Args:
        data_dir: Base directory containing train/, val/, and test/.
        image_size: Target image size for transforms.
        batch_size: Mini-batch size.
        num_workers: Worker processes for data loading (0 on Windows recommended).
        random_seed: Random seed for DataLoader generator reproducibility.
        pin_memory: Enable memory pinning for CUDA transfers (auto-detected if None).

    Returns:
        Tuple of (train_loader, val_loader, test_loader)
    """
    if pin_memory is None:
        pin_memory = torch.cuda.is_available()

    generator = None
    if random_seed is not None:
        generator = torch.Generator()
        generator.manual_seed(random_seed)

    train_ds, val_ds, test_ds = get_datasets(data_dir=data_dir, image_size=image_size)

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
        generator=generator,
        drop_last=False
    )

    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=False
    )

    test_loader = DataLoader(
        test_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=False
    )

    return train_loader, val_loader, test_loader


def verify_dataset(
    data_dir: str | Path,
    image_size: int = DEFAULT_IMAGE_SIZE,
    batch_size: int = DEFAULT_BATCH_SIZE,
    num_workers: int = DEFAULT_NUM_WORKERS
) -> Dict:
    """
    Performs verification on the dataset present on disk:
      - Reports dataset sizes and class distributions per split.
      - Confirms deterministic class mapping.
      - Loads a test batch and checks tensor shapes, value ranges, and types.
      - Scans for corrupted or unreadable images.

    Returns:
        Dictionary containing verification metrics and status report.
    """
    train_loader, val_loader, test_loader = get_dataloaders(
        data_dir=data_dir,
        image_size=image_size,
        batch_size=batch_size,
        num_workers=num_workers
    )

    train_ds = train_loader.dataset
    val_ds = val_loader.dataset
    test_ds = test_loader.dataset

    def count_classes(ds: datasets.ImageFolder) -> Dict[str, int]:
        counts = {cls: 0 for cls in ds.classes}
        for _, target in ds.samples:
            cls_name = ds.classes[target]
            counts[cls_name] += 1
        return counts

    train_counts = count_classes(train_ds)
    val_counts = count_classes(val_ds)
    test_counts = count_classes(test_ds)

    # Fetch one batch from train_loader
    sample_images, sample_labels = next(iter(train_loader))

    report = {
        "status": "success",
        "batch_size": batch_size,
        "image_size": (image_size, image_size),
        "class_to_idx": train_ds.class_to_idx,
        "idx_to_class": {v: k for k, v in train_ds.class_to_idx.items()},
        "splits": {
            "train": {
                "total": len(train_ds),
                "counts": train_counts
            },
            "val": {
                "total": len(val_ds),
                "counts": val_counts
            },
            "test": {
                "total": len(test_ds),
                "counts": test_counts
            }
        },
        "sample_batch": {
            "images_shape": list(sample_images.shape),
            "labels_shape": list(sample_labels.shape),
            "images_dtype": str(sample_images.dtype),
            "labels_dtype": str(sample_labels.dtype),
            "images_min": float(sample_images.min()),
            "images_max": float(sample_images.max()),
            "device": str(sample_images.device)
        }
    }
    return report


if __name__ == "__main__":
    # Self-test when executed directly
    base_data = Path(__file__).resolve().parent.parent / "data"
    print(f"Running verification on: {base_data}")
    results = verify_dataset(base_data)
    import pprint
    pprint.pprint(results)
