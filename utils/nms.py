# utils/nms.py
"""
Non-Maximum Suppression utilities.
Removes duplicate detections of the same object.
"""

import torch
from torch import Tensor
from torchvision.ops import nms as torchvision_nms
from torchvision.ops import batched_nms


def apply_nms(
    boxes:      Tensor,
    scores:     Tensor,
    iou_thresh: float = 0.5,
) -> Tensor:
    """
    Apply NMS to a set of boxes.

    Args:
        boxes      : Tensor [N, 4]  xyxy format
        scores     : Tensor [N]     confidence scores
        iou_thresh : Remove boxes with IoU > this with a higher-scoring box

    Returns:
        keep : Tensor [K]  indices of boxes to keep (K <= N)
    """
    if boxes.numel() == 0:
        return torch.zeros(0, dtype=torch.long)

    # torchvision's NMS is CUDA-accelerated — much faster than pure Python
    keep = torchvision_nms(boxes, scores, iou_thresh)
    return keep


def apply_nms_per_class(
    boxes:      Tensor,
    scores:     Tensor,
    labels:     Tensor,
    iou_thresh: float = 0.5,
    score_thresh: float = 0.05,
) -> Tensor:
    """
    Apply NMS separately per class.
    Prevents a high-scoring car from suppressing a nearby person.

    Args:
        boxes        : Tensor [N, 4]
        scores       : Tensor [N]
        labels       : Tensor [N]    class indices
        iou_thresh   : NMS IoU threshold
        score_thresh : Remove boxes below this score before NMS

    Returns:
        keep : Tensor [K]  indices to keep
    """
    # First filter by score threshold
    score_mask = scores > score_thresh
    boxes  = boxes[score_mask]
    scores = scores[score_mask]
    labels = labels[score_mask]

    if boxes.numel() == 0:
        return torch.zeros(0, dtype=torch.long)

    # batched_nms treats each class independently
    # by offsetting boxes by class_id * large_number
    keep = batched_nms(boxes, scores, labels, iou_thresh)
    return keep


def soft_nms_scores(
    boxes:      Tensor,
    scores:     Tensor,
    iou_thresh: float = 0.5,
    sigma:      float = 0.5,
    method:     str   = "gaussian",
) -> Tensor:
    """
    Soft-NMS: instead of removing boxes, REDUCE their scores.
    Better for crowded scenes where objects genuinely overlap.

    Args:
        boxes      : Tensor [N, 4]
        scores     : Tensor [N]
        iou_thresh : threshold for score reduction
        sigma      : gaussian decay parameter
        method     : "gaussian" or "linear"

    Returns:
        updated_scores : Tensor [N]  — scores after soft suppression
    """
    scores = scores.clone()
    N      = len(boxes)

    for i in range(N):
        # Compare box i against all subsequent boxes
        for j in range(i + 1, N):
            iou = _iou_single(boxes[i], boxes[j])

            if iou > iou_thresh:
                if method == "gaussian":
                    # Smoothly decay score based on overlap
                    decay = torch.exp(torch.tensor(-iou**2 / sigma))
                else:
                    # Linear decay
                    decay = torch.tensor(1 - iou)

                # Decay the lower-scoring box
                if scores[i] > scores[j]:
                    scores[j] *= decay
                else:
                    scores[i] *= decay

    return scores


def _iou_single(box_a: Tensor, box_b: Tensor) -> float:
    """IoU between two single boxes (internal helper)."""
    x1 = max(box_a[0], box_b[0])
    y1 = max(box_a[1], box_b[1])
    x2 = min(box_a[2], box_b[2])
    y2 = min(box_a[3], box_b[3])
    inter = max(0, x2-x1) * max(0, y2-y1)
    area_a = (box_a[2]-box_a[0]) * (box_a[3]-box_a[1])
    area_b = (box_b[2]-box_b[0]) * (box_b[3]-box_b[1])
    union  = area_a + area_b - inter
    return (inter / (union + 1e-6)).item()