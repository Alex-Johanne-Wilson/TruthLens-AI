import json
import torch
from torch.utils.data import DataLoader
from pathlib import Path
from tqdm import tqdm
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

from dataset import DeepfakeDataset
from model import build_deepfake_model

def evaluate():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = base_dir / "data" / "deepfake"
    out_dir = base_dir / "outputs"
    checkpoints_dir = out_dir / "checkpoints"
    eval_dir = out_dir / "evaluation"
    eval_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = checkpoints_dir / "deepfake_resnet18.pth"
    if not model_path.exists():
        raise FileNotFoundError(f"Model checkpoint not found at {model_path}")
        
    test_dataset = DeepfakeDataset(str(data_dir), split="test")
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=4)
    
    model = build_deepfake_model(pretrained=False, device=device)
    model.load_state_dict(torch.load(str(model_path), map_location=device))
    model.eval()
    
    all_preds = []
    all_probs = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in tqdm(test_loader, desc="Evaluating on Test Set"):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)[:, 1] # Probability of 'real' (class 1)
            _, predicted = torch.max(outputs, 1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
    # Metrics
    acc = accuracy_score(all_labels, all_preds)
    prec = precision_score(all_labels, all_preds, zero_division=0)
    rec = recall_score(all_labels, all_preds, zero_division=0)
    f1 = f1_score(all_labels, all_preds, zero_division=0)
    cm = confusion_matrix(all_labels, all_preds).tolist()
    
    try:
        roc_auc = roc_auc_score(all_labels, all_probs)
    except ValueError:
        roc_auc = 0.0 # Handle case where only one class is present in test
        
    metrics = {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "roc_auc": roc_auc,
        "confusion_matrix": cm,
        "label_mapping": {"0": "fake", "1": "real"}
    }
    
    print(f"Test Accuracy: {acc:.4f}")
    print(f"Test F1: {f1:.4f}")
    print(f"Test ROC AUC: {roc_auc:.4f}")
    
    metrics_path = eval_dir / "deepfake_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {metrics_path}")

if __name__ == "__main__":
    evaluate()
