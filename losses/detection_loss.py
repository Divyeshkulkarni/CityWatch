# losses/detection_loss.py
"""
Detection Loss Module
─────────────────────
Torchvision's Faster-RCNN computes all 4 losses internally.
This module provides:
  1. A wrapper to extract and combine losses cleanly
  2. A loss tracker to monitor training progress
  3. Utility to weight individual losses differently if needed
  4. Smoothed loss history for TensorBoard logging
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import torch


# ── Loss Weights ──────────────────────────────────────────────────────────────
# Default: all losses equally weighted
# Increase a weight if that component needs more emphasis
DEFAULT_LOSS_WEIGHTS = {
    "loss_objectness":    1.0,   # RPN: object vs background
    "loss_rpn_box_reg":   1.0,   # RPN: rough box regression
    "loss_classifier":    1.0,   # ROI: class prediction
    "loss_box_reg":       1.0,   # ROI: precise box regression
}


def compute_total_loss(
    loss_dict:    Dict[str, torch.Tensor],
    weights:      Dict[str, float] = None,
) -> torch.Tensor:
    """
    Combine the 4 Faster-RCNN losses into a single scalar.

    Args:
        loss_dict : Dict returned by model(images, targets) in train mode
        weights   : Optional per-loss weights (default: all 1.0)

    Returns:
        total_loss : Single scalar tensor — what the optimizer minimizes
    """
    if weights is None:
        weights = DEFAULT_LOSS_WEIGHTS

    total = sum(
        weights.get(name, 1.0) * value
        for name, value in loss_dict.items()
    )
    return total


# ── Loss Tracker ──────────────────────────────────────────────────────────────

@dataclass
class LossTracker:
    """
    Tracks loss values across batches within an epoch.
    Provides running averages and history for logging.

    Usage:
        tracker = LossTracker()
        for batch in loader:
            loss_dict = model(images, targets)
            tracker.update(loss_dict)
        epoch_summary = tracker.get_averages()
        tracker.reset()
    """
    history: List[Dict[str, float]] = field(default_factory=list)
    _running: Dict[str, float]      = field(default_factory=dict)
    _count:   int                   = 0

    def update(self, loss_dict: Dict[str, torch.Tensor]):
        """Add one batch of losses."""
        self._count += 1
        for name, value in loss_dict.items():
            v = value.item()
            if name not in self._running:
                self._running[name] = 0.0
            self._running[name] += v

    def get_averages(self) -> Dict[str, float]:
        """Return average loss per component over all tracked batches."""
        if self._count == 0:
            return {}
        return {
            name: val / self._count
            for name, val in self._running.items()
        }

    def get_total_average(self, weights: Dict[str, float] = None) -> float:
        """Return weighted average of total loss."""
        avgs    = self.get_averages()
        weights = weights or DEFAULT_LOSS_WEIGHTS
        return sum(weights.get(k, 1.0) * v for k, v in avgs.items())

    def reset(self):
        """Call at the start of each epoch."""
        self.history.append(self.get_averages())
        self._running = {}
        self._count   = 0

    def print_epoch_summary(self, epoch: int):
        """Pretty print loss summary for one epoch."""
        avgs  = self.get_averages()
        total = self.get_total_average()

        print(f"\n  Epoch {epoch} — Loss Summary")
        print(f"  {'─'*40}")
        for name, value in avgs.items():
            bar = "█" * int(20 * value / max(total, 1e-6))
            print(f"  {name:<25} {value:.4f}  {bar}")
        print(f"  {'─'*40}")
        print(f"  {'Total':<25} {total:.4f}")

    def get_tensorboard_dict(self) -> Dict[str, float]:
        """Format for TensorBoard logging."""
        avgs = self.get_averages()
        avgs["total"] = self.get_total_average()
        return avgs