# training/evaluator.py
"""
Evaluator
─────────
Runs the model on the validation set and computes:
  - mAP@0.5     (PASCAL VOC standard)
  - mAP@0.5:0.95 (COCO standard)
  - AP per class
  - AP for small/medium/large objects

Two evaluation modes:
  1. Quick eval  — our own mAP implementation (from utils/metrics.py)
  2. COCO eval   — official pycocotools evaluation (used for final results)
"""

import torch
import time
import json
import numpy as np
from pathlib import Path
from torch.amp import autocast
from collections import defaultdict
from pycocotools.coco     import COCO
from pycocotools.cocoeval import COCOeval

from utils.metrics import compute_map
from dataset.coco_dataset import LABEL_TO_NAME, COCO_ID_TO_LABEL


# Reverse map: our compact label → original COCO category ID
LABEL_TO_COCO_ID = {v: k for k, v in COCO_ID_TO_LABEL.items()}


@torch.no_grad()
def evaluate_one_epoch(
    model,
    data_loader,
    device,
    epoch        = 0,
    score_thresh = 0.05,
    writer       = None,
) -> dict:
    """
    Run model on validation set and compute mAP.

    Args:
        model        : FasterRCNN in eval mode
        data_loader  : validation DataLoader (batch_size=1)
        device       : torch device
        epoch        : current epoch (for logging)
        score_thresh : minimum score to keep a detection
        writer       : TensorBoard SummaryWriter (optional)

    Returns:
        metrics dict with mAP, AP_per_class, etc.
    """
    model.eval()

    all_predictions   = []
    all_ground_truths = []
    eval_start        = time.time()

    print(f"\n  [Eval] Running evaluation on "
          f"{len(data_loader)} images...")

    for batch_idx, (images, targets) in enumerate(data_loader):

        # Move to device
        images = [img.to(device) for img in images]

        # Forward pass — no targets needed in eval mode
        with autocast("cuda", enabled=(device.type == "cuda")):
            outputs = model(images)

        # Collect predictions and ground truths
        for output, target in zip(outputs, targets):

            img_id = target["image_id"].item()

            # ── Filter predictions ────────────────────────────────────────
            scores = output["scores"]
            keep   = scores >= score_thresh

            pred = {
                "image_id": img_id,
                "boxes":    output["boxes"][keep].cpu(),
                "labels":   output["labels"][keep].cpu(),
                "scores":   output["scores"][keep].cpu(),
            }

            gt = {
                "image_id": img_id,
                "boxes":    target["boxes"].cpu(),
                "labels":   target["labels"].cpu(),
            }

            all_predictions.append(pred)
            all_ground_truths.append(gt)

        # Progress update every 100 images
        if (batch_idx + 1) % 100 == 0:
            print(f"  [Eval] Processed {batch_idx + 1}/"
                  f"{len(data_loader)} images")

    eval_time = time.time() - eval_start
    print(f"  [Eval] Forward passes done in {eval_time:.1f}s")

    # ── Compute mAP ───────────────────────────────────────────────────────────
    print(f"  [Eval] Computing mAP...")

    results = compute_map(
        predictions   = all_predictions,
        ground_truths = all_ground_truths,
        num_classes   = len(LABEL_TO_NAME) - 1,  # exclude background
        iou_threshold = 0.5,
        label_names   = LABEL_TO_NAME,
    )

    # Print results
    print(results["summary"])
    print(f"  [Eval] Total time: {time.time() - eval_start:.1f}s\n")

    # TensorBoard logging
    if writer is not None:
        writer.add_scalar("mAP/val_mAP50",   results["mAP"], epoch)
        for cls, ap in results["AP_per_class"].items():
            name = LABEL_TO_NAME.get(cls, f"cls_{cls}")
            writer.add_scalar(f"AP/{name}", ap, epoch)

    return results


@torch.no_grad()
def evaluate_coco_official(
    model,
    data_loader,
    device,
    ann_file:    str,
    score_thresh: float = 0.05,
) -> dict:
    """
    Official COCO evaluation using pycocotools.
    Produces the standard 12-metric COCO report.

    Args:
        model        : FasterRCNN in eval mode
        data_loader  : validation DataLoader
        device       : torch device
        ann_file     : path to COCO annotation JSON
        score_thresh : minimum score threshold

    Returns:
        dict with coco_map50, coco_map5095
    """
    model.eval()
    coco_gt   = COCO(ann_file)
    coco_preds = []

    print(f"\n  [COCO Eval] Running official COCO evaluation...")

    for images, targets in data_loader:
        images  = [img.to(device) for img in images]

        with autocast("cuda", enabled=(device.type == "cuda")):
            outputs = model(images)

        for output, target in zip(outputs, targets):
            img_id = target["image_id"].item()
            scores = output["scores"]
            keep   = scores >= score_thresh

            boxes  = output["boxes"][keep].cpu().numpy()
            labels = output["labels"][keep].cpu().numpy()
            scores = output["scores"][keep].cpu().numpy()

            for box, label, score in zip(boxes, labels, scores):
                # Convert xyxy → xywh for COCO format
                x1, y1, x2, y2 = box
                w = x2 - x1
                h = y2 - y1

                # Convert compact label back to COCO category ID
                coco_cat_id = LABEL_TO_COCO_ID.get(int(label), int(label))

                coco_preds.append({
                    "image_id":    img_id,
                    "category_id": coco_cat_id,
                    "bbox":        [float(x1), float(y1),
                                    float(w),  float(h)],
                    "score":       float(score),
                })

    if len(coco_preds) == 0:
        print("  [COCO Eval] No predictions — model may need more training")
        return {"coco_map50": 0.0, "coco_map5095": 0.0}

    # Load predictions into COCO API
    coco_dt   = coco_gt.loadRes(coco_preds)
    coco_eval = COCOeval(coco_gt, coco_dt, "bbox")

    # Only evaluate on our target categories
    coco_eval.params.catIds = list(LABEL_TO_COCO_ID.values())
    coco_eval.evaluate()
    coco_eval.accumulate()

    print("\n  === Official COCO Metrics ===")
    coco_eval.summarize()

    # Extract key metrics
    # stats[0] = mAP@0.5:0.95
    # stats[1] = mAP@0.5
    map5095 = float(coco_eval.stats[0])
    map50   = float(coco_eval.stats[1])

    print(f"\n  mAP@0.50      : {map50:.4f}")
    print(f"  mAP@0.50:0.95 : {map5095:.4f}")

    return {
        "coco_map50":   map50,
        "coco_map5095": map5095,
        "all_stats":    coco_eval.stats.tolist(),
    }


def format_eval_summary(
    epoch:   int,
    metrics: dict,
    losses:  dict = None,
) -> str:
    """
    Format a clean summary string for one evaluation epoch.
    Useful for logging to file or printing to console.
    """
    lines = []
    lines.append(f"\n{'='*50}")
    lines.append(f"  Epoch {epoch} — Evaluation Summary")
    lines.append(f"{'='*50}")

    if losses:
        total = sum(losses.values())
        lines.append(f"\n  Losses:")
        for name, val in losses.items():
            lines.append(f"    {name:<25} : {val:.4f}")
        lines.append(f"    {'Total':<25} : {total:.4f}")

    lines.append(f"\n  Detection Metrics:")
    lines.append(f"    {'mAP@0.50':<25} : "
                 f"{metrics.get('mAP', 0):.4f}")

    if "AP_per_class" in metrics:
        lines.append(f"\n  Per-class AP:")
        for cls, ap in metrics["AP_per_class"].items():
            name = LABEL_TO_NAME.get(cls, f"cls_{cls}")
            bar  = "█" * int(ap * 20)
            lines.append(f"    {name:<15} {ap:.4f}  {bar}")

    lines.append(f"\n{'='*50}\n")
    return "\n".join(lines)