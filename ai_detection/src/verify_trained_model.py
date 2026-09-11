import json
import torch
from pathlib import Path
import sys
base_dir = Path(__file__).resolve().parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from src.model import build_model
from src.dataset import get_dataloaders

ckpt_path = Path("outputs/checkpoints/best_model.pth")
history_path = Path("outputs/training_history.json")

print("1. Checking checkpoint file existence...")
assert ckpt_path.exists(), "best_model.pth does not exist!"
print("Checkpoint size:", ckpt_path.stat().st_size, "bytes")

print("2. Loading checkpoint...")
ckpt = torch.load(ckpt_path, weights_only=False)
print("Checkpoint metadata keys:", list(ckpt.keys()))
print("Best epoch recorded:", ckpt["epoch"])
print("Best val F1 in checkpoint:", ckpt["best_val_f1"])
print("Class mapping in checkpoint:", ckpt["class_to_idx"])

print("3. Instantiating model and loading state dict...")
model = build_model(num_classes=2, pretrained=False, device="cpu")
model.load_state_dict(ckpt["model_state_dict"])
model.eval()
print("Model state dict loaded successfully!")

# Check that all parameters are finite
for name, param in model.named_parameters():
    assert torch.isfinite(param).all(), f"Non-finite parameter found in {name}"
print("All model parameters are finite and healthy!")

print("4. Running real forward pass on an actual validation batch...")
_, val_loader, _ = get_dataloaders(Path("data"), batch_size=16, num_workers=0)
val_images, val_targets = next(iter(val_loader))

with torch.no_grad():
    logits = model(val_images)

print("Val batch input shape:", val_images.shape)
print("Val batch output logits shape:", logits.shape)
assert logits.shape == (16, 2)
assert torch.isfinite(logits).all()
preds = torch.argmax(logits, dim=1)
print("Sample predicted classes:", preds[:8].tolist())
print("Sample ground truth:", val_targets[:8].tolist())
print("Forward pass on trained checkpoint verified successfully!")

print("5. Verifying training history JSON...")
assert history_path.exists(), "training_history.json does not exist!"
with open(history_path, "r", encoding="utf-8") as f:
    history = json.load(f)

print("History epochs recorded:", len(history["epoch"]))
print("History keys:", list(history.keys()))
for ep_idx in range(len(history["epoch"])):
    print(f"  Epoch {history['epoch'][ep_idx]}: Train Loss={history['train_loss'][ep_idx]}, Val Loss={history['val_loss'][ep_idx]}, Val Acc={history['val_accuracy'][ep_idx]}, Val F1={history['val_f1'][ep_idx]}")
