# utils/iou.py
"""
IoU (Intersection over Union) utilities.
Used in: RPN matching, ROI matching, NMS, mAP evaluation.
"""

import torch
from torch import Tensor


def compute_iou(boxes_a: Tensor, boxes_b: Tensor) -> Tensor:
    """
    Compute pairwise IoU between two sets of boxes.

    Args:
        boxes_a : Tensor [N, 4]  xyxy format
        boxes_b : Tensor [M, 4]  xyxy format

    Returns:
        iou     : Tensor [N, M]  — iou[i,j] = IoU between boxes_a[i] and boxes_b[j]

    Example:
        boxes_a has 3 predicted boxes
        boxes_b has 2 ground truth boxes
        Returns a [3, 2] matrix of IoU values
    """
    # Expand dims for broadcasting: [N,1,4] and [1,M,4]
    a = boxes_a.unsqueeze(1)   # [N, 1, 4]
    b = boxes_b.unsqueeze(0)   # [1, M, 4]

    # Intersection top-left = max of top-lefts
    # Intersection bottom-right = min of bottom-rights
    inter_x1 = torch.max(a[..., 0], b[..., 0])
    inter_y1 = torch.max(a[..., 1], b[..., 1])
    inter_x2 = torch.min(a[..., 2], b[..., 2])
    inter_y2 = torch.min(a[..., 3], b[..., 3])

    # Intersection area — clamp at 0 (boxes might not overlap)
    inter_w    = (inter_x2 - inter_x1).clamp(min=0)
    inter_h    = (inter_y2 - inter_y1).clamp(min=0)
    inter_area = inter_w * inter_h   # [N, M]

    # Individual areas
    area_a = ((boxes_a[:, 2] - boxes_a[:, 0]) *
               (boxes_a[:, 3] - boxes_a[:, 1])).unsqueeze(1)  # [N, 1]
    area_b = ((boxes_b[:, 2] - boxes_b[:, 0]) *
               (boxes_b[:, 3] - boxes_b[:, 1])).unsqueeze(0)  # [1, M]

    # Union area
    union_area = area_a + area_b - inter_area   # [N, M]

    # IoU — add small epsilon to avoid division by zero
    iou = inter_area / (union_area + 1e-6)

    return iou


def compute_iou_single(box_a: Tensor, box_b: Tensor) -> float:
    """
    Compute IoU between two single boxes.

    Args:
        box_a, box_b : Tensor [4]  xyxy format

    Returns:
        iou : float
    """
    x1 = torch.max(box_a[0], box_b[0])
    y1 = torch.max(box_a[1], box_b[1])
    x2 = torch.min(box_a[2], box_b[2])
    y2 = torch.min(box_a[3], box_b[3])

    inter = (x2 - x1).clamp(0) * (y2 - y1).clamp(0)
    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    union  = area_a + area_b - inter

    return (inter / (union + 1e-6)).item()


def match_boxes_to_gt(
    proposals:   Tensor,
    gt_boxes:    Tensor,
    fg_thresh:   float = 0.5,
    bg_thresh:   float = 0.5,
) -> tuple[Tensor, Tensor]:
    """
    Match each proposal to a ground truth box based on IoU.
    Used to assign labels to proposals during training.

    Args:
        proposals  : Tensor [N, 4]  predicted/proposed boxes
        gt_boxes   : Tensor [M, 4]  ground truth boxes
        fg_thresh  : IoU above this → positive match (foreground)
        bg_thresh  : IoU below this → negative match (background)

    Returns:
        matched_gt_idx : Tensor [N]  — which GT box each proposal matched to
        match_quality  : Tensor [N]  — IoU value of the match
                         (-1 = background, -2 = ignored/between thresholds)
    """
    if gt_boxes.numel() == 0:
        return (
            torch.full((len(proposals),), -1, dtype=torch.long),
            torch.zeros(len(proposals)),
        )

    iou_matrix = compute_iou(proposals, gt_boxes)   # [N, M]

    # Best GT match for each proposal
    match_quality, matched_gt_idx = iou_matrix.max(dim=1)   # [N]

    # Mark background (IoU too low)
    below_bg = match_quality < bg_thresh
    matched_gt_idx[below_bg] = -1

    # Mark ignored (between thresholds — neither clearly fg nor bg)
    between = (match_quality >= bg_thresh) & (match_quality < fg_thresh)
    matched_gt_idx[between] = -2

    return matched_gt_idx, match_quality