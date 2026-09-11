"""
Evaluation pipeline for the trained AI-generated image detector on held-out test data.
Computes Accuracy, Precision, Recall, F1, ROC-AUC, Confusion Matrix,
classification report, and misclassification error analysis.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)
from torch.utils.data import DataLoader

# Ensure ai_detection base is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from src.dataset import CLASS_TO_IDX, IDX_TO_CLASS, get_dataloaders
    from src.model import build_model
    from src.utils import get_device, set_seed
except ImportError:
    from dataset import CLASS_TO_IDX, IDX_TO_CLASS, get_dataloaders
    from model import build_model
    from utils import get_device, set_seed


def load_trained_model(
    checkpoint_path: str | Path,
    device: Optional[torch.device] = None
) -> Tuple[nn.Module, Dict]:
    """
    Loads trained checkpoint weights into the EfficientNet-B0 detector.
    Verifies parameter integrity and returns model and checkpoint metadata.
    """
    device = get_device(device)
    ckpt_path = Path(checkpoint_path)
    if not ckpt_path.exists():
        raise FileNotFoundError(f"Trained checkpoint not found at: {ckpt_path}")

    checkpoint = torch.load(ckpt_path, map_location=device, weights_only=False)
    
    # Instantiate model architecture (2 classes)
    model = build_model(num_classes=2, pretrained=False, device=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    # Integrity verification
    for name, param in model.named_parameters():
        if not torch.isfinite(param).all():
            raise ValueError(f"Non-finite parameters detected in layer: {name}")

    return model, checkpoint


def evaluate_dataset(
    model: nn.Module,
    data_loader: DataLoader,
    device: torch.device
) -> Dict:
    """
    Runs inference across all test samples, collecting targets, predictions,
    raw probabilities, and paths of misclassified samples.
    """
    model.eval()
    all_targets: List[int] = []
    all_preds: List[int] = []
    all_probs_real: List[float] = []
    all_probs_ai: List[float] = []
    misclassified: List[Dict] = []

    dataset = data_loader.dataset
    current_sample_idx = 0

    with torch.no_grad():
        for images, targets in data_loader:
            images = images.to(device)
            targets = targets.to(device)

            logits = model(images)
            probabilities = torch.softmax(logits, dim=1)
            preds = torch.argmax(probabilities, dim=1)

            probs_cpu = probabilities.cpu().numpy()
            preds_cpu = preds.cpu().numpy()
            targets_cpu = targets.cpu().numpy()

            batch_size = images.size(0)
            for i in range(batch_size):
                tgt = int(targets_cpu[i])
                prd = int(preds_cpu[i])
                p_ai = float(probs_cpu[i][0])
                p_real = float(probs_cpu[i][1])

                all_targets.append(tgt)
                all_preds.append(prd)
                all_probs_ai.append(p_ai)
                all_probs_real.append(p_real)

                if prd != tgt:
                    img_path = dataset.samples[current_sample_idx + i][0]
                    confidence = p_real if prd == 1 else p_ai
                    misclassified.append({
                        "file_path": str(img_path),
                        "file_name": Path(img_path).name,
                        "actual_label": tgt,
                        "actual_class": IDX_TO_CLASS[tgt],
                        "predicted_label": prd,
                        "predicted_class": IDX_TO_CLASS[prd],
                        "confidence": round(confidence, 4),
                        "prob_ai_generated": round(p_ai, 4),
                        "prob_real": round(p_real, 4)
                    })

            current_sample_idx += batch_size

    y_true = np.array(all_targets)
    y_pred = np.array(all_preds)
    y_scores = np.array(all_probs_real)  # Probability of positive class (Real = 1)

    # Core evaluation metrics
    acc = float(accuracy_score(y_true, y_pred))
    roc_auc = float(roc_auc_score(y_true, y_scores))

    # Binary metrics (pos_label=1: Real)
    prec_bin, rec_bin, f1_bin, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", pos_label=1, zero_division=0
    )

    # Macro & Weighted metrics
    prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    prec_wt, rec_wt, f1_wt, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )

    # Confusion Matrix:
    # rows: actual [ai_generated (0), real (1)]
    # cols: predicted [ai_generated (0), real (1)]
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])

    # Per-class metrics
    per_class_prec, per_class_rec, per_class_f1, per_class_supp = precision_recall_fscore_support(
        y_true, y_pred, labels=[0, 1], zero_division=0
    )

    clf_report = classification_report(
        y_true, y_pred, target_names=["ai_generated", "real"], output_dict=True, zero_division=0
    )

    results = {
        "dataset_size": len(y_true),
        "class_mapping": CLASS_TO_IDX,
        "metrics": {
            "accuracy": round(acc, 5),
            "precision": round(float(prec_bin), 5),
            "recall": round(float(rec_bin), 5),
            "f1": round(float(f1_bin), 5),
            "roc_auc": round(roc_auc, 5),
            "macro_avg": {
                "precision": round(float(prec_macro), 5),
                "recall": round(float(rec_macro), 5),
                "f1": round(float(f1_macro), 5)
            },
            "weighted_avg": {
                "precision": round(float(prec_wt), 5),
                "recall": round(float(rec_wt), 5),
                "f1": round(float(f1_wt), 5)
            }
        },
        "per_class": {
            "ai_generated": {
                "label": 0,
                "precision": round(float(per_class_prec[0]), 5),
                "recall": round(float(per_class_rec[0]), 5),
                "f1": round(float(per_class_f1[0]), 5),
                "support": int(per_class_supp[0])
            },
            "real": {
                "label": 1,
                "precision": round(float(per_class_prec[1]), 5),
                "recall": round(float(per_class_rec[1]), 5),
                "f1": round(float(per_class_f1[1]), 5),
                "support": int(per_class_supp[1])
            }
        },
        "confusion_matrix": {
            "matrix": cm.tolist(),
            "labels": ["ai_generated", "real"],
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "true_positives": tp,
            "correct_predictions": tn + tp,
            "incorrect_predictions": fp + fn
        },
        "misclassified_count": len(misclassified),
        "classification_report": clf_report
    }

    return results, misclassified, cm


def plot_confusion_matrix(cm: np.ndarray, output_path: Path) -> None:
    """
    Renders and saves a clean, annotated confusion matrix heatmap.
    """
    plt.figure(figsize=(6.5, 5.5))
    annot = np.array([
        [f"TN: {cm[0, 0]}", f"FP: {cm[0, 1]}"],
        [f"FN: {cm[1, 0]}", f"TP: {cm[1, 1]}"]
    ])

    sns.heatmap(
        cm,
        annot=annot,
        fmt="",
        cmap="Blues",
        cbar=True,
        xticklabels=["AI-Generated (0)", "Real (1)"],
        yticklabels=["AI-Generated (0)", "Real (1)"],
        annot_kws={"size": 13, "weight": "bold"}
    )

    plt.title("TruthLens AI - AI Image Detector Test Confusion Matrix", fontsize=12, pad=12, weight="bold")
    plt.xlabel("Predicted Class", fontsize=11, labelpad=8)
    plt.ylabel("Actual Class", fontsize=11, labelpad=8)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Confusion matrix plot saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate TruthLens AI-generated image detector on held-out test set")
    parser.add_argument("--data-dir", type=str, default="data", help="Base data directory")
    parser.add_argument("--checkpoint", type=str, default="outputs/checkpoints/best_model.pth", help="Checkpoint path")
    parser.add_argument("--batch-size", type=int, default=16, help="Evaluation batch size")
    parser.add_argument("--output-dir", type=str, default="outputs/evaluation", help="Directory to save evaluation artifacts")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    set_seed(args.seed)
    device = get_device()

    base_dir = Path(__file__).resolve().parent.parent
    data_path = base_dir / args.data_dir
    checkpoint_path = base_dir / args.checkpoint
    output_dir = base_dir / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading checkpoint from: {checkpoint_path}")
    model, checkpoint = load_trained_model(checkpoint_path, device=device)
    print(f"Model loaded successfully (trained epoch: {checkpoint.get('epoch')}, validation F1: {checkpoint.get('best_val_f1'):.4f})")

    print(f"Initializing test DataLoader from: {data_path / 'test'}")
    _, _, test_loader = get_dataloaders(
        data_dir=data_path,
        batch_size=args.batch_size,
        num_workers=0,
        random_seed=args.seed
    )
    print(f"Test samples: {len(test_loader.dataset)} across {len(test_loader)} batches")

    print("Running evaluation across all test samples...")
    results, misclassified, cm = evaluate_dataset(model, test_loader, device=device)
    results["checkpoint_path"] = str(checkpoint_path)

    # Save test_results.json
    results_json_path = output_dir / "test_results.json"
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Test results saved to: {results_json_path}")

    # Save confusion_matrix.png
    cm_png_path = output_dir / "confusion_matrix.png"
    plot_confusion_matrix(cm, cm_png_path)

    # Save misclassified.json
    misc_json_path = output_dir / "misclassified.json"
    with open(misc_json_path, "w", encoding="utf-8") as f:
        json.dump(misclassified, f, indent=2)
    print(f"Misclassified samples report saved to: {misc_json_path}")

    # Print summary report
    print("\n" + "=" * 60)
    print("TRUTHLENS AI - TEST SET EVALUATION REPORT")
    print("=" * 60)
    print(f"Total Test Samples: {results['dataset_size']} (AI: 375, Real: 375)")
    print(f"Overall Accuracy:   {results['metrics']['accuracy'] * 100:.2f}%")
    print(f"Precision (Real):   {results['metrics']['precision'] * 100:.2f}%")
    print(f"Recall (Real):      {results['metrics']['recall'] * 100:.2f}%")
    print(f"F1-Score (Real):    {results['metrics']['f1'] * 100:.2f}%")
    print(f"ROC-AUC:            {results['metrics']['roc_auc'] * 100:.2f}%")
    print("-" * 60)
    print("Confusion Matrix:")
    print(f"  True Negatives (AI correctly identified):     {results['confusion_matrix']['true_negatives']}")
    print(f"  False Positives (AI wrongly flagged as Real): {results['confusion_matrix']['false_positives']}")
    print(f"  False Negatives (Real wrongly flagged as AI): {results['confusion_matrix']['false_negatives']}")
    print(f"  True Positives (Real correctly identified):   {results['confusion_matrix']['true_positives']}")
    print(f"  Total Correct:   {results['confusion_matrix']['correct_predictions']} / {results['dataset_size']}")
    print(f"  Total Incorrect: {results['confusion_matrix']['incorrect_predictions']} / {results['dataset_size']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
