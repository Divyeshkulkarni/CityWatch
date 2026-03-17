# utils/box_utils.py
"""
Bounding box format conversion utilities.

Three formats used across the codebase:
  xyxy   : [x1, y1, x2, y2]   top-left + bottom-right  (torchvision standard)
  xywh   : [x, y, w, h]       top-left + width/height  (COCO JSON format)
  cxcywh : [cx, cy, w, h]     center + width/height    (some model internals)
"""

import torch
from torch import Tensor


def xyxy_to_xywh(boxes: Tensor) -> Tensor:
    """
    [x1, y1, x2, y2] → [x, y, w, h]
    torchvision format → COCO format
    """
    x1, y1, x2, y2 = boxes.unbind(dim=-1)
    return torch.stack([x1, y1, x2 - x1, y2 - y1], dim=-1)


def xywh_to_xyxy(boxes: Tensor) -> Tensor:
    """
    [x, y, w, h] → [x1, y1, x2, y2]
    COCO format → torchvision format
    """
    x, y, w, h = boxes.unbind(dim=-1)
    return torch.stack([x, y, x + w, y + h], dim=-1)


def xyxy_to_cxcywh(boxes: Tensor) -> Tensor:
    """
    [x1, y1, x2, y2] → [cx, cy, w, h]
    torchvision format → center format
    """
    x1, y1, x2, y2 = boxes.unbind(dim=-1)
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    w  = x2 - x1
    h  = y2 - y1
    return torch.stack([cx, cy, w, h], dim=-1)


def cxcywh_to_xyxy(boxes: Tensor) -> Tensor:
    """
    [cx, cy, w, h] → [x1, y1, x2, y2]
    center format → torchvision format
    """
    cx, cy, w, h = boxes.unbind(dim=-1)
    x1 = cx - w / 2
    y1 = cy - h / 2
    x2 = cx + w / 2
    y2 = cy + h / 2
    return torch.stack([x1, y1, x2, y2], dim=-1)


def clip_boxes_to_image(boxes: Tensor, image_size: tuple) -> Tensor:
    """
    Clip boxes so they don't extend outside image boundaries.

    Args:
        boxes      : Tensor [N, 4]  xyxy format
        image_size : (height, width)

    Returns:
        clipped boxes : Tensor [N, 4]
    """
    H, W = image_size
    x1 = boxes[:, 0].clamp(min=0, max=W)
    y1 = boxes[:, 1].clamp(min=0, max=H)
    x2 = boxes[:, 2].clamp(min=0, max=W)
    y2 = boxes[:, 3].clamp(min=0, max=H)
    return torch.stack([x1, y1, x2, y2], dim=1)


def filter_small_boxes(boxes: Tensor, min_size: float = 1.0) -> Tensor:
    """
    Remove boxes that are too small to be meaningful.

    Args:
        boxes    : Tensor [N, 4]  xyxy format
        min_size : minimum width AND height in pixels

    Returns:
        keep : Tensor of indices to keep
    """
    w = boxes[:, 2] - boxes[:, 0]
    h = boxes[:, 3] - boxes[:, 1]
    keep = torch.where((w >= min_size) & (h >= min_size))[0]
    return keep


def box_area(boxes: Tensor) -> Tensor:
    """
    Compute area of boxes.

    Args:
        boxes : Tensor [N, 4]  xyxy format
    Returns:
        area  : Tensor [N]
    """
    return (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])