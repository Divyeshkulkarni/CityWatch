# utils/metrics.py
"""
Detection metrics — mAP computation.
Measures overall model quality across all classes.
"""

import torch
import numpy as np
from collections import defaultdict
from typing import List, Dict


def compute_ap(
    recalls:    np.ndarray,
    precisions: np.ndarray,
) -> float:
    """
    Compute Average Precision using the 11-point interpolation method.
    Area under the Precision-Recall curve.

    Args:
        recalls    : array of recall values    (sorted ascending)
        precisions : array of precision values

    Returns:
        ap : float — average precision for one class
    """
    # Add sentinel values at start and end
    recalls    = np.concatenate([[0.0], recalls,    [1.0]])
    precisions = np.concatenate([[0.0], precisions, [0.0]])

    # Make precision monotonically decreasing
    for i in range(len(precisions) - 2, -1, -1):
        precisions[i] = max(precisions[i], precisions[i + 1])

    # Find points where recall changes
    recall_change = np.where(recalls[1:] != recalls[:-1])[0] + 1

    # Area = sum of rectangles
    ap = np.sum(
        (recalls[recall_change] - recalls[recall_change - 1]) *
         precisions[recall_change]
    )
    return float(ap)


def compute_map(
    predictions: List[Dict],
    ground_truths: List[Dict],
    num_classes: int,
    iou_threshold: float = 0.5,
    label_names: Dict[int, str] = None,
) -> Dict:
    """
    Compute mAP across all classes.

    Args:
        predictions   : List of dicts per image, each with:
                          "boxes"    Tensor [N, 4]
                          "labels"   Tensor [N]
                          "scores"   Tensor [N]
                          "image_id" int
        ground_truths : List of dicts per image, each with:
                          "boxes"    Tensor [M, 4]
                          "labels"   Tensor [M]
                          "image_id" int
        num_classes   : Total number of classes (excluding background)
        iou_threshold : IoU threshold for a detection to count as TP
        label_names   : Optional dict mapping label index → class name

    Returns:
        results : dict with keys:
                    "mAP"        overall mean AP
                    "AP_per_class" dict of AP per class
                    "summary"    printable string
    """
    from utils.iou import compute_iou

    # Build GT lookup: image_id → list of (box, label, matched)
    gt_by_image = defaultdict(list)
    for gt in ground_truths:
        img_id = gt["image_id"]
        for box, label in zip(gt["boxes"], gt["labels"]):
            gt_by_image[img_id].append({
                "box":     box,
                "label":   label.item(),
                "matched": False,
            })

    # Collect all predictions sorted by score (descending)
    all_preds = []
    for pred in predictions:
        img_id = pred["image_id"]
        for box, label, score in zip(pred["boxes"], pred["labels"], pred["scores"]):
            all_preds.append({
                "image_id": img_id,
                "box":      box,
                "label":    label.item(),
                "score":    score.item(),
            })

    all_preds.sort(key=lambda x: x["score"], reverse=True)

    # Compute AP per class
    ap_per_class = {}

    for cls in range(1, num_classes + 1):
        # Filter predictions and GTs for this class
        cls_preds = [p for p in all_preds if p["label"] == cls]
        n_gt      = sum(
            1 for gts in gt_by_image.values()
            for g in gts if g["label"] == cls
        )

        if n_gt == 0:
            ap_per_class[cls] = 0.0
            continue

        # Reset matched flags for this class
        for gts in gt_by_image.values():
            for g in gts:
                g["matched"] = False

        tp_list = []
        fp_list = []

        for pred in cls_preds:
            img_id  = pred["image_id"]
            gt_list = [g for g in gt_by_image[img_id] if g["label"] == cls]

            if len(gt_list) == 0:
                tp_list.append(0)
                fp_list.append(1)
                continue

            # Find best matching GT
            gt_boxes = torch.stack([g["box"] for g in gt_list])
            iou_vals = compute_iou(
                pred["box"].unsqueeze(0), gt_boxes
            ).squeeze(0)

            best_iou, best_idx = iou_vals.max(0)

            if best_iou >= iou_threshold and not gt_list[best_idx]["matched"]:
                tp_list.append(1)
                fp_list.append(0)
                gt_list[best_idx]["matched"] = True
            else:
                tp_list.append(0)
                fp_list.append(1)

        # Cumulative TP and FP
        tp_cum = np.cumsum(tp_list)
        fp_cum = np.cumsum(fp_list)

        recalls    = tp_cum / (n_gt + 1e-6)
        precisions = tp_cum / (tp_cum + fp_cum + 1e-6)

        ap_per_class[cls] = compute_ap(recalls, precisions)

    # Mean AP
    mean_ap = float(np.mean(list(ap_per_class.values())))

    # Build summary string
    lines = [f"\n  mAP@{iou_threshold:.2f} = {mean_ap:.4f}\n"]
    lines.append(f"  {'Class':<15} {'AP':>8}")
    lines.append(f"  {'-'*25}")
    for cls, ap in ap_per_class.items():
        name = label_names.get(cls, f"class_{cls}") if label_names else f"class_{cls}"
        bar  = "█" * int(ap * 20)
        lines.append(f"  {name:<15} {ap:>8.4f}  {bar}")

    return {
        "mAP":          mean_ap,
        "AP_per_class": ap_per_class,
        "summary":      "\n".join(lines),
    }