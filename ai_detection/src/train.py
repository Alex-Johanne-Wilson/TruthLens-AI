"""
Training pipeline for EfficientNet-B0 on AI-generated vs. Real image classification.
Supports CrossEntropyLoss, AdamW, LR scheduling, validation tracking,
best checkpoint saving (by validation F1), early stopping, and history export.
"""

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader

import sys
# Ensure ai_detection base is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from src.dataset import CLASS_TO_IDX, IDX_TO_CLASS, get_dataloaders
    from src.model import build_model
    from src.utils import compute_classification_metrics, get_device, set_seed
except ImportError:
    from dataset import CLASS_TO_IDX, IDX_TO_CLASS, get_dataloaders
    from model import build_model
    from utils import compute_classification_metrics, get_device, set_seed


class Trainer:
    """
    Manages the training, validation, checkpointing, and early stopping lifecycles.
    """

    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        optimizer: torch.optim.Optimizer,
        criterion: nn.Module,
        scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
        device: Optional[torch.device] = None,
        checkpoint_dir: str | Path = "outputs/checkpoints",
        history_path: str | Path = "outputs/training_history.json",
        early_stopping_patience: int = 5,
        metric_average: str = "binary",
        config: Optional[Dict] = None,
    ) -> None:
        self.device = get_device(device)
        self.model = model.to(self.device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.optimizer = optimizer
        self.criterion = criterion
        self.scheduler = scheduler
        self.early_stopping_patience = early_stopping_patience
        self.metric_average = metric_average
        self.config = config or {}

        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = Path(history_path)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

        self.best_checkpoint_path = self.checkpoint_dir / "best_model.pth"

        # Tracking state
        self.best_val_f1: float = -1.0
        self.best_val_acc: float = 0.0
        self.best_epoch: int = 0
        self.epochs_without_improvement: int = 0
        self.history: Dict[str, list] = {
            "epoch": [],
            "train_loss": [],
            "val_loss": [],
            "train_accuracy": [],
            "val_accuracy": [],
            "train_precision": [],
            "val_precision": [],
            "train_recall": [],
            "val_recall": [],
            "train_f1": [],
            "val_f1": [],
            "learning_rate": []
        }

    def train_one_epoch(self, max_batches: Optional[int] = None) -> Tuple[float, Dict[str, float]]:
        """
        Runs one training epoch over train_loader.
        """
        self.model.train()
        running_loss = 0.0
        all_preds = []
        all_targets = []

        batch_count = 0
        for batch_idx, (images, targets) in enumerate(self.train_loader):
            if max_batches is not None and batch_idx >= max_batches:
                break

            images = images.to(self.device)
            targets = targets.to(self.device)

            self.optimizer.zero_grad()
            outputs = self.model(images)
            loss = self.criterion(outputs, targets)
            loss.backward()
            self.optimizer.step()

            running_loss += loss.item() * images.size(0)
            preds = torch.argmax(outputs, dim=1)

            all_preds.extend(preds.detach().cpu().tolist())
            all_targets.extend(targets.detach().cpu().tolist())
            batch_count += 1

        total_samples = len(all_targets) if len(all_targets) > 0 else 1
        epoch_loss = running_loss / total_samples
        metrics = compute_classification_metrics(all_targets, all_preds, average=self.metric_average)
        return epoch_loss, metrics

    @torch.no_grad()
    def evaluate(self, data_loader: DataLoader, max_batches: Optional[int] = None) -> Tuple[float, Dict[str, float]]:
        """
        Evaluates the model on the provided data_loader.
        """
        self.model.eval()
        running_loss = 0.0
        all_preds = []
        all_targets = []

        for batch_idx, (images, targets) in enumerate(data_loader):
            if max_batches is not None and batch_idx >= max_batches:
                break

            images = images.to(self.device)
            targets = targets.to(self.device)

            outputs = self.model(images)
            loss = self.criterion(outputs, targets)

            running_loss += loss.item() * images.size(0)
            preds = torch.argmax(outputs, dim=1)

            all_preds.extend(preds.detach().cpu().tolist())
            all_targets.extend(targets.detach().cpu().tolist())

        total_samples = len(all_targets) if len(all_targets) > 0 else 1
        epoch_loss = running_loss / total_samples
        metrics = compute_classification_metrics(all_targets, all_preds, average=self.metric_average)
        return epoch_loss, metrics

    def save_checkpoint(self, epoch: int, val_loss: float, val_metrics: Dict[str, float]) -> None:
        """
        Saves the best model checkpoint to disk.
        """
        checkpoint = {
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scheduler_state_dict": self.scheduler.state_dict() if self.scheduler else None,
            "val_loss": val_loss,
            "val_metrics": val_metrics,
            "best_val_f1": self.best_val_f1,
            "class_to_idx": CLASS_TO_IDX,
            "idx_to_class": IDX_TO_CLASS,
            "config": self.config
        }
        torch.save(checkpoint, self.best_checkpoint_path)
        print(f"  --> Saved new best checkpoint to {self.best_checkpoint_path} (Val F1: {self.best_val_f1:.4f})")

    def save_history(self) -> None:
        """
        Writes training history to a JSON file.
        """
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)

    def train(
        self,
        num_epochs: int,
        max_train_batches: Optional[int] = None,
        max_val_batches: Optional[int] = None
    ) -> Dict:
        """
        Executes the full training loop with early stopping.
        """
        start_time = time.time()
        print(f"\nStarting training on device: {self.device}")
        print(f"Total Epochs: {num_epochs} | Early Stopping Patience: {self.early_stopping_patience}")
        print("-" * 65)

        for epoch in range(1, num_epochs + 1):
            epoch_start = time.time()
            current_lr = self.optimizer.param_groups[0]["lr"]

            # Training Phase
            train_loss, train_metrics = self.train_one_epoch(max_batches=max_train_batches)

            # Validation Phase
            val_loss, val_metrics = self.evaluate(self.val_loader, max_batches=max_val_batches)

            # Step scheduler if configured
            if self.scheduler is not None:
                if isinstance(self.scheduler, ReduceLROnPlateau):
                    self.scheduler.step(val_loss)
                else:
                    self.scheduler.step()

            # Record history
            self.history["epoch"].append(epoch)
            self.history["train_loss"].append(round(train_loss, 5))
            self.history["val_loss"].append(round(val_loss, 5))
            self.history["train_accuracy"].append(round(train_metrics["accuracy"], 5))
            self.history["val_accuracy"].append(round(val_metrics["accuracy"], 5))
            self.history["train_precision"].append(round(train_metrics["precision"], 5))
            self.history["val_precision"].append(round(val_metrics["precision"], 5))
            self.history["train_recall"].append(round(train_metrics["recall"], 5))
            self.history["val_recall"].append(round(val_metrics["recall"], 5))
            self.history["train_f1"].append(round(train_metrics["f1"], 5))
            self.history["val_f1"].append(round(val_metrics["f1"], 5))
            self.history["learning_rate"].append(current_lr)

            elapsed = time.time() - epoch_start

            # Epoch progress logging
            print(
                f"Epoch {epoch:02d}/{num_epochs:02d} [{elapsed:.1f}s] | "
                f"Train Loss: {train_loss:.4f}, Acc: {train_metrics['accuracy']:.4f}, F1: {train_metrics['f1']:.4f} | "
                f"Val Loss: {val_loss:.4f}, Acc: {val_metrics['accuracy']:.4f}, F1: {val_metrics['f1']:.4f} | "
                f"LR: {current_lr:.6f}"
            )

            # Checkpoint selection based on Validation F1
            val_f1 = val_metrics["f1"]
            if val_f1 > self.best_val_f1:
                self.best_val_f1 = val_f1
                self.best_val_acc = val_metrics["accuracy"]
                self.best_epoch = epoch
                self.epochs_without_improvement = 0
                self.save_checkpoint(epoch, val_loss, val_metrics)
            else:
                self.epochs_without_improvement += 1
                if self.epochs_without_improvement >= self.early_stopping_patience:
                    print(f"\n[Early Stopping Triggered] No improvement in validation F1 for {self.early_stopping_patience} consecutive epochs.")
                    break

        total_time = time.time() - start_time
        self.save_history()

        summary = {
            "best_epoch": self.best_epoch,
            "best_val_f1": self.best_val_f1,
            "best_val_accuracy": self.best_val_acc,
            "total_training_time_seconds": round(total_time, 2),
            "checkpoint_path": str(self.best_checkpoint_path),
            "history_path": str(self.history_path)
        }

        print("-" * 65)
        print("Training Complete:")
        print(f"  Best Epoch: {summary['best_epoch']}")
        print(f"  Best Val F1: {summary['best_val_f1']:.4f}")
        print(f"  Best Val Acc: {summary['best_val_accuracy']:.4f}")
        print(f"  Total Duration: {summary['total_training_time_seconds']}s")
        print(f"  Checkpoint: {summary['checkpoint_path']}")
        print(f"  History: {summary['history_path']}\n")

        return summary


def parse_args():
    parser = argparse.ArgumentParser(description="Train EfficientNet-B0 for AI Image Detection")
    parser.add_argument("--data-dir", type=str, default="data", help="Path to data directory")
    parser.add_argument("--batch-size", type=int, default=32, help="Mini-batch size")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate for AdamW")
    parser.add_argument("--weight-decay", type=float, default=1e-4, help="Weight decay for AdamW")
    parser.add_argument("--patience", type=int, default=3, help="Early stopping patience")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--num-workers", type=int, default=0, help="DataLoader worker count (0 for Windows)")
    parser.add_argument("--checkpoint-dir", type=str, default="outputs/checkpoints", help="Directory for checkpoints")
    parser.add_argument("--history-path", type=str, default="outputs/training_history.json", help="Path for history JSON")
    parser.add_argument("--pretrained", action="store_true", default=True, help="Load ImageNet-pretrained weights")
    parser.add_argument("--metric-average", type=str, default="binary", choices=["binary", "macro"], help="F1 averaging strategy")
    return parser.parse_args()


def main():
    args = parse_args()
    set_seed(args.seed)

    base_dir = Path(__file__).resolve().parent.parent
    data_path = base_dir / args.data_dir
    checkpoint_dir = base_dir / args.checkpoint_dir
    history_path = base_dir / args.history_path

    config = vars(args)

    print("Initializing DataLoaders...")
    train_loader, val_loader, _ = get_dataloaders(
        data_dir=data_path,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        random_seed=args.seed
    )

    device = get_device()
    print(f"Initializing EfficientNet-B0 (Pretrained={args.pretrained}, Device={device})...")
    model = build_model(num_classes=2, pretrained=args.pretrained, device=device)

    criterion = nn.CrossEntropyLoss()
    optimizer = AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=1)

    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        optimizer=optimizer,
        criterion=criterion,
        scheduler=scheduler,
        device=device,
        checkpoint_dir=checkpoint_dir,
        history_path=history_path,
        early_stopping_patience=args.patience,
        metric_average=args.metric_average,
        config=config
    )

    trainer.train(num_epochs=args.epochs)


if __name__ == "__main__":
    main()
