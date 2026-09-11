# TruthLens AI - AI-Generated Image Detection Module

This module is the AI-generated image detection subsystem of the **TruthLens AI** computer vision forensics project.

## Directory Structure

```text
ai_detection/
├── data/
│   ├── dataset_info.json  # Metadata recording dataset provenance, splits, counts, seed, and label mapping
│   ├── train/
│   │   ├── real/          # 1,750 authentic images
│   │   └── ai_generated/  # 1,750 AI-generated images
│   ├── val/
│   │   ├── real/          # 375 authentic images
│   │   └── ai_generated/  # 375 AI-generated images
│   └── test/
│       ├── real/          # 375 authentic images
│       └── ai_generated/  # 375 AI-generated images
├── models/                # Saved model weights, checkpoints (.pt, .pth), and architecture configs
├── notebooks/             # Jupyter notebooks for EDA, error analysis, and feature visualization
├── outputs/               # Evaluation plots, confusion matrices, logs, and prediction reports
├── src/
│   ├── __init__.py        # Package initialization
│   ├── setup_dataset.py   # Dataset extraction and partitioning script
│   ├── dataset.py         # Custom PyTorch Dataset, dataloaders, and augmentation pipelines
│   ├── model.py           # EfficientNet-B0 detector architecture and factory functions
│   ├── train.py           # Training loop, optimizer, loss function, and checkpointing
│   ├── evaluate.py        # Evaluation routines, test metrics (ROC-AUC, F1, Precision, Recall)
│   ├── inference.py       # Standalone inference script for test images
│   └── utils.py           # Common helpers: device setup, logging, seed setting, plotting
├── requirements.txt       # Python dependencies required for this module
└── README.md              # Documentation and usage guide
```

## Dataset Acquisition & Setup

The dataset is built from the Hugging Face dataset [`Parveshiiii/AI-vs-Real`](https://huggingface.co/datasets/Parveshiiii/AI-vs-Real).

### Dataset Properties
- **Source**: `Parveshiiii/AI-vs-Real`
- **Total Subset Size**: 5,000 images (2,500 real, 2,500 AI-generated)
- **Class Labels**:
  - `0`: `ai_generated`
  - `1`: `real`
- **Partitioning**: 70% Train (3,500), 15% Validation (750), 15% Test (750)
- **Random Seed**: `42`
- **Image Preservation**: Unaltered raw bytes extracted directly from source Parquet files (no resizing, compression, or modification).

### Reproducing Dataset Acquisition
To re-run the dataset extraction and setup:
```bash
cd ai_detection
python src/setup_dataset.py
```
This downloads only the required shards (`train-00000-of-00005.parquet` and `train-00001-of-00005.parquet`), samples disjoint subsets using seed `42`, and generates `data/dataset_info.json`.

## Preprocessing & DataLoader Usage

The PyTorch dataset pipeline is implemented in [`src/dataset.py`](file:///c:/Users/Alex%20Wilson/OneDrive/Documents/A.Projects/Truthlens-AI/ai_detection/src/dataset.py), configured for EfficientNet-B0 standards.

### Transforms Pipeline
- **Input Dimensions**: $224 \times 224$ (bilinear interpolation).
- **Color Channels**: Explicit RGB conversion for grayscale (`L`), palette (`P`), and `RGBA` formats.
- **Normalization**: Standard ImageNet mean `[0.485, 0.456, 0.406]` and std `[0.229, 0.224, 0.225]`.
- **Training Augmentations**: Resizing to $256 \times 256$ followed by `RandomCrop(224)`, `RandomHorizontalFlip(p=0.5)`, and subtle `ColorJitter(brightness=0.05, contrast=0.05)`.
- **Validation & Test Preprocessing**: Deterministic resizing to $256 \times 256$ followed by `CenterCrop(224)`.

### Class Mapping
- `0` $\rightarrow$ `ai_generated`
- `1` $\rightarrow$ `real`

### Python Usage
```python
from pathlib import Path
from src.dataset import get_dataloaders, verify_dataset

# Factory function to build DataLoaders
data_dir = Path("data")
train_loader, val_loader, test_loader = get_dataloaders(
    data_dir=data_dir,
    image_size=224,
    batch_size=32,
    num_workers=0,  # 0 recommended on Windows
    random_seed=42
)

# Run verification and inspection
report = verify_dataset(data_dir=data_dir, batch_size=32)
print(report)
```

To run dataset verification from the terminal:
```bash
cd ai_detection
python src/dataset.py
```

## Model Architecture (EfficientNet-B0)

The model is defined in [`src/model.py`](file:///c:/Users/Alex%20Wilson/OneDrive/Documents/A.Projects/Truthlens-AI/ai_detection/src/model.py).

### Specifications
- **Backbone**: `torchvision.models.efficientnet_b0` pretrained on ImageNet-1k (`DEFAULT` / `IMAGENET1K_V1`).
- **Classification Head**: Replaced with `Sequential(Dropout(p=0.2), Linear(in_features=1280, out_features=2))`.
- **Output Classes**: `2` (`0 = ai_generated`, `1 = real`).
- **Total Parameters**: 4,010,110 (all parameters trainable by default; freezing strategy deferred to training phase).
- **Input Dimensions**: `(3, 224, 224)` tensor with ImageNet normalization.

### Python Usage
```python
from src.model import build_model, verify_model

# Instantiate model with ImageNet pretraining
model = build_model(num_classes=2, pretrained=True)

# Run diagnostic verification
diagnostics = verify_model(data_dir="data")
print(diagnostics)
```

To run model verification from the terminal:
```bash
cd ai_detection
python src/model.py
```

## Model Training Pipeline

The training pipeline is implemented in [`src/train.py`](file:///c:/Users/Alex%20Wilson/OneDrive/Documents/A.Projects/Truthlens-AI/ai_detection/src/train.py) with early stopping, validation tracking, checkpointing, and history logging.

### Key Features
- **Loss Function**: `CrossEntropyLoss`.
- **Optimizer**: `AdamW` (configurable learning rate and weight decay).
- **LR Scheduler**: `ReduceLROnPlateau` (halves learning rate when validation loss plateaus).
- **Model Selection**: Selects and saves the best model checkpoint based on **Validation F1-score**.
- **Early Stopping**: Halts training if validation F1 does not improve for `patience` consecutive epochs.
- **Artifacts Saved**:
  - Best model checkpoint: `outputs/checkpoints/best_model.pth`
  - Training metrics history: `outputs/training_history.json`

### Training Command & Arguments
```bash
cd ai_detection
python src/train.py --epochs 10 --batch-size 32 --lr 0.0003 --weight-decay 0.0001 --patience 3 --seed 42
```

#### Configurable CLI Arguments:
- `--data-dir`: Base directory containing data splits (default: `data`).
- `--batch-size`: Mini-batch size (default: `32`).
- `--epochs`: Total number of training epochs (default: `10`).
- `--lr`: Initial AdamW learning rate (default: `0.0003`).
- `--weight-decay`: Weight decay factor (default: `0.0001`).
- `--patience`: Early stopping patience (default: `3`).
- `--seed`: Random seed for reproducibility (default: `42`).
- `--num-workers`: Number of data loader workers (default: `0`).
- `--checkpoint-dir`: Directory for saving checkpoints (default: `outputs/checkpoints`).
- `--history-path`: Path for output JSON metrics history (default: `outputs/training_history.json`).
- `--metric-average`: F1 calculation strategy (`binary` or `macro`, default: `binary`).

### Actual Training Benchmark & Model Performance (CPU)
Training completed on the 5,000-image dataset (`3,500` train, `750` validation):
- **Epochs Run**: 7 (Early stopping halted training at patience 3)
- **Best Epoch**: **Epoch 4**
- **Validation Accuracy**: **98.93%**
- **Validation F1-Score**: **0.9894**
- **Validation Precision**: **98.67%**
- **Validation Recall**: **99.20%**
- **Final Checkpoint Artifact**: `outputs/checkpoints/best_model.pth`
- **History Metrics Log**: `outputs/training_history.json`
- **Total Training Duration**: 2,046.06 seconds (~34.1 minutes)

## Final Test-Set Evaluation

The held-out test set evaluation is implemented in [`src/evaluate.py`](file:///c:/Users/Alex%20Wilson/OneDrive/Documents/A.Projects/Truthlens-AI/ai_detection/src/evaluate.py). It evaluates the best checkpoint (`outputs/checkpoints/best_model.pth`) across all **750 unseen test images** (375 Real, 375 AI-Generated).

### Execution Command
```bash
cd ai_detection
python src/evaluate.py --checkpoint outputs/checkpoints/best_model.pth --batch-size 16
```

### Final Held-Out Test Results
- **Total Test Images**: 750 (Balanced: 375 Real, 375 AI-Generated)
- **Overall Accuracy**: **99.07%** (743 / 750 correct)
- **Precision (Real)**: **98.68%**
- **Recall (Real)**: **99.47%** (373 / 375 real images identified)
- **F1-Score (Real)**: **99.07%**
- **ROC-AUC**: **99.93%**

### Confusion Matrix Breakdown

# Grad-CAM Explainability

The `src/gradcam.py` script generates Grad‑CAM visualizations that highlight the image regions most influential to the model’s prediction. This helps users understand why the detector classified an image as AI‑generated or real.

## CLI Usage

```bash
python src/gradcam.py --image <path_to_image> --output <output_dir>
```

- `--image`: Path to a single test image.
- `--output`: Directory to save the generated overlay (defaults to `outputs/gradcam`).

### Example Commands

```bash
# Correctly classified AI‑generated image
python src/gradcam.py --image data/test/ai_generated/ai_generated_2125.jpg --output outputs/gradcam

# Correctly classified real image
python src/gradcam.py --image data/test/real/real_2125.jpg --output outputs/gradcam

# Misclassified example (from misclassified.json)
python src/gradcam.py --image data/test/ai_generated/ai_generated_2133.jpg --output outputs/gradcam
```

Generated visualizations are saved as `gradcam_<image_name>.png` in the chosen output directory. Sample outputs are available in `outputs/gradcam/`.
- **True Negatives (`TN`)**: 370 (AI correctly identified)
- **False Positives (`FP`)**: 5 (AI incorrectly predicted as Real)
- **False Negatives (`FN`)**: 2 (Real incorrectly predicted as AI)
- **True Positives (`TP`)**: 373 (Real correctly identified)

### Evaluation Artifacts
- **Metrics & Classification Report**: `outputs/evaluation/test_results.json`
- **Confusion Matrix Visualization**: `outputs/evaluation/confusion_matrix.png`
- **Misclassified Analysis**: `outputs/evaluation/misclassified.json` (7 misclassified images analyzed)





