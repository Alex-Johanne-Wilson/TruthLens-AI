"""
Utility helper functions: seed setting, device detection, and classification metric calculations.
"""

import os
import random
from typing import Dict, Union

import numpy as np
import torch
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


def set_seed(seed: int = 42) -> None:
    """
    Set random seeds across Python, NumPy, and PyTorch for reproducible runs.
    """
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def get_device(requested_device: Union[str, torch.device, None] = None) -> torch.device:
    """
    Resolves the torch.device, falling back to CPU if CUDA is unavailable.
    """
    if requested_device is not None:
        device = torch.device(requested_device)
        if device.type == "cuda" and not torch.cuda.is_available():
            return torch.device("cpu")
        return device
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def compute_classification_metrics(
    y_true: Union[list, np.ndarray, torch.Tensor],
    y_pred: Union[list, np.ndarray, torch.Tensor],
    average: str = "binary"
) -> Dict[str, float]:
    """
    Compute accuracy, precision, recall, and F1 score.
    
    Args:
        y_true: Ground truth target labels (0 or 1).
        y_pred: Predicted class labels (0 or 1).
        average: Averaging strategy. Defaults to 'binary' (evaluates class 1: Real),
                 or 'macro' for balanced multi-class aggregation.
                 
    Returns:
        Dictionary containing:
          - accuracy
          - precision
          - recall
          - f1
          - f1_macro
    """
    if isinstance(y_true, torch.Tensor):
        y_true = y_true.detach().cpu().numpy()
    if isinstance(y_pred, torch.Tensor):
        y_pred = y_pred.detach().cpu().numpy()

    y_true = np.asarray(y_true).ravel()
    y_pred = np.asarray(y_pred).ravel()

    acc = float(accuracy_score(y_true, y_pred))

    # Binary metrics (pos_label=1: Real)
    prec_bin, rec_bin, f1_bin, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0, pos_label=1
    )

    # Macro metrics (average across 0: ai_generated and 1: real)
    prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )

    return {
        "accuracy": acc,
        "precision": float(prec_macro if average == "macro" else prec_bin),
        "recall": float(rec_macro if average == "macro" else rec_bin),
        "f1": float(f1_macro if average == "macro" else f1_bin),
        "f1_macro": float(f1_macro)
    }
