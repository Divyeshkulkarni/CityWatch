# utils/visualization.py
"""
Visualization utilities for detection results.
Used during training to visually inspect model predictions.
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Dict, Optional

LABEL_COLORS = {
    "person":     "lime",
    "bicycle":    "yellow",
    "car":        "red",
    "motorcycle": "magenta",
    "bus":        "cyan",
    "truck":      "orange",
    "background": "white",
}

def denormalize_image(tensor: torch.Tensor) -> np.ndarray:
    """
    Undo ImageNet normalization for display.
    tensor : [3, H, W] float32
    returns: [H, W, 3] uint8
    """
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std  = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    img  = (tensor.cpu() * std + mean).clamp(0, 1)
    return (img.permute(1, 2, 0).numpy() * 255).astype(np.uint8)


def draw_boxes(
    ax,
    boxes:      torch.Tensor,
    labels:     torch.Tensor,
    scores:     Optional[torch.Tensor] = None,
    label_names: Dict[int, str] = None,
    color:      str = None,
):
    """Draw boxes on a matplotlib axis."""
    for i, (box, label) in enumerate(zip(boxes, labels)):
        x1, y1, x2, y2 = box.tolist()
        name  = label_names.get(label.item(), f"cls_{label}") if label_names else str(label.item())
        clr   = color or LABEL_COLORS.get(name, "white")
        score = scores[i].item() if scores is not None else None

        rect = patches.Rectangle(
            (x1, y1), x2-x1, y2-y1,
            linewidth=2, edgecolor=clr, facecolor="none"
        )
        ax.add_patch(rect)

        label_text = f"{name} {score:.2f}" if score else name
        ax.text(x1, y1-4, label_text, color=clr, fontsize=8,
                fontweight="bold",
                bbox=dict(facecolor="black", alpha=0.3, pad=1))


def visualize_predictions(
    image:       torch.Tensor,
    predictions: Dict,
    ground_truth: Dict = None,
    label_names: Dict[int, str] = None,
    score_thresh: float = 0.5,
    title:       str = "",
):
    """
    Side-by-side comparison of ground truth vs predictions.

    Args:
        image        : [3, H, W] normalized tensor
        predictions  : dict with boxes, labels, scores
        ground_truth : dict with boxes, labels (optional)
        label_names  : label index → class name mapping
        score_thresh : only show predictions above this score
        title        : plot title
    """
    img_np = denormalize_image(image)

    if ground_truth is not None:
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        ax_gt, ax_pred = axes

        # Ground Truth
        ax_gt.imshow(img_np)
        draw_boxes(ax_gt, ground_truth["boxes"],
                   ground_truth["labels"],
                   label_names=label_names, color="lime")
        ax_gt.set_title(f"Ground Truth ({len(ground_truth['boxes'])} objects)",
                        fontsize=11)
        ax_gt.axis("off")
    else:
        fig, ax_pred = plt.subplots(1, 1, figsize=(10, 8))

    # Filter predictions by score
    if len(predictions["scores"]) > 0:
        keep   = predictions["scores"] >= score_thresh
        p_boxes  = predictions["boxes"][keep]
        p_labels = predictions["labels"][keep]
        p_scores = predictions["scores"][keep]
    else:
        p_boxes = p_labels = p_scores = torch.zeros(0)

    # Predictions
    ax_pred.imshow(img_np)
    if len(p_boxes) > 0:
        draw_boxes(ax_pred, p_boxes, p_labels, p_scores,
                   label_names=label_names, color=None)
    ax_pred.set_title(f"Predictions ({len(p_boxes)} detections @ score>{score_thresh})",
                      fontsize=11)
    ax_pred.axis("off")

    if title:
        plt.suptitle(title, fontsize=13, y=1.01)

    plt.tight_layout()
    plt.show()