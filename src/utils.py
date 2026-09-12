# ai_detection/src/utils.py
"""Utility functions for model evaluation, metrics calculation, and API data serialization."""

import logging
from typing import Dict, Union, Any, List
import numpy as np
import torch
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score

logger = logging.getLogger(__name__)


def sanitize_for_serialization(obj: Any) -> Any:
    """Recursively convert NumPy scalars, NumPy arrays, and PyTorch tensors
    into JSON-serializable standard Python types (int, float, bool, str, list, dict, None).

    Parameters
    ----------
    obj : Any
        Object or data structure to convert.

    Returns
    -------
    Any
        JSON-serializable version of the input object.
    """
    if obj is None:
        return None

    # Handle PyTorch Tensors
    if isinstance(obj, torch.Tensor):
        detached = obj.detach().cpu()
        if detached.ndim == 0:
            # scalar tensor — convert directly and return
            scalar = detached.item()
            return bool(scalar) if isinstance(scalar, bool) else (int(scalar) if isinstance(scalar, int) else float(scalar))
        else:
            return sanitize_for_serialization(detached.numpy().tolist())

    # Handle NumPy ndarrays
    if isinstance(obj, np.ndarray):
        return sanitize_for_serialization(obj.tolist())

    # Handle NumPy scalar types (np.bool8 was removed in NumPy 2.x; np.bool_ covers it)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.complexfloating):
        return complex(obj)

    # Handle standard collections recursively
    if isinstance(obj, dict):
        return {str(k): sanitize_for_serialization(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [sanitize_for_serialization(v) for v in obj]

    # Return standard primitives as-is
    return obj


def calculate_metrics(
    y_true: Union[list, np.ndarray, torch.Tensor],
    y_pred: Union[list, np.ndarray, torch.Tensor],
    y_prob: Union[list, np.ndarray, torch.Tensor, None] = None,
) -> Dict[str, float]:
    """Calculate classification metrics: accuracy, precision, recall, f1, and optional roc_auc.

    Parameters
    ----------
    y_true : list or ndarray or Tensor
        Ground truth binary labels (0 or 1).
    y_pred : list or ndarray or Tensor
        Predicted binary labels (0 or 1).
    y_prob : list or ndarray or Tensor, optional
        Predicted probabilities for the positive class (1).

    Returns
    -------
    Dict[str, float]
        Dictionary containing metric names and float values.
    """
    if isinstance(y_true, torch.Tensor):
        y_true = y_true.cpu().numpy()
    if isinstance(y_pred, torch.Tensor):
        y_pred = y_pred.cpu().numpy()
    if isinstance(y_prob, torch.Tensor):
        y_prob = y_prob.cpu().numpy()

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    acc = float(accuracy_score(y_true, y_pred))
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )

    metrics = {
        "accuracy": float(acc),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
    }

    if y_prob is not None:
        y_prob = np.asarray(y_prob)
        try:
            auc = float(roc_auc_score(y_true, y_prob))
            metrics["roc_auc"] = auc
        except ValueError as e:
            logger.warning(f"Could not calculate ROC-AUC: {e}")
            metrics["roc_auc"] = 0.0

    return metrics
