# inference.py
"""
Inference Pipeline
──────────────────
Runs the trained detection model on:
  - Single image
  - Folder of images
  - Video file
  - Live webcam feed

Usage:
  python inference.py --source image.jpg
  python inference.py --source video.mp4
  python inference.py --source 0           (webcam)
  python inference.py --source images/     (folder)
  python inference.py --source image.jpg --checkpoint checkpoints/best_model.pth
"""

import os
import sys
import cv2
import time
import torch
import argparse
import numpy as np
from pathlib import Path
from PIL import Image
import torchvision.transforms.functional as F

sys.path.insert(0, str(Path(__file__).parent))

import configs.config as cfg
from model.detector      import build_detector
from training.evaluator  import evaluate_one_epoch
from utils.box_utils     import clip_boxes_to_image
from utils.nms           import apply_nms_per_class
from dataset.coco_dataset import LABEL_TO_NAME


# ── Class colours (BGR for OpenCV) ───────────────────────────────────────────
CLASS_COLORS_BGR = {
    "person":     (0,   255, 0),
    "bicycle":    (0,   255, 255),
    "car":        (0,   0,   255),
    "motorcycle": (255, 0,   200),
    "bus":        (255, 165, 0),
    "truck":      (200, 0,   200),
}
DEFAULT_COLOR = (200, 200, 200)


# ── Preprocessing ─────────────────────────────────────────────────────────────

def preprocess_image(image_input) -> tuple:
    """
    Prepare an image for inference.

    Args:
        image_input : file path (str) OR BGR numpy array (from cv2)

    Returns:
        tensor    : FloatTensor [3, H, W] normalized
        orig_size : (H, W) of original image
    """
    if isinstance(image_input, str):
        # Load from file
        pil_img = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, np.ndarray):
        # Convert BGR (OpenCV) → RGB (PIL)
        rgb     = cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
    else:
        raise ValueError(f"Unsupported input type: {type(image_input)}")

    orig_size = (pil_img.height, pil_img.width)

    # ToTensor: PIL [H,W,3] uint8 → FloatTensor [3,H,W] in [0,1]
    tensor = F.to_tensor(pil_img)

    # Normalize with ImageNet stats — MUST match training
    tensor = F.normalize(
        tensor,
        mean = [0.485, 0.456, 0.406],
        std  = [0.229, 0.224, 0.225],
    )

    return tensor, orig_size


# ── Post-processing ───────────────────────────────────────────────────────────

def postprocess_detections(
    output:       dict,
    orig_size:    tuple,
    score_thresh: float = 0.5,
    nms_thresh:   float = 0.4,
) -> dict:
    """
    Clean up raw model output.

    Steps:
      1. Filter by score threshold
      2. Apply per-class NMS
      3. Clip boxes to image boundary

    Args:
        output       : raw model output dict (boxes, labels, scores)
        orig_size    : (H, W) of original image
        score_thresh : minimum confidence to keep
        nms_thresh   : IoU threshold for NMS

    Returns:
        cleaned dict with boxes, labels, scores, class_names
    """
    boxes  = output["boxes"]
    labels = output["labels"]
    scores = output["scores"]

    # Step 1: Score threshold
    keep   = scores >= score_thresh
    boxes  = boxes[keep]
    labels = labels[keep]
    scores = scores[keep]

    if len(boxes) == 0:
        return {
            "boxes":       torch.zeros((0, 4)),
            "labels":      torch.zeros((0,), dtype=torch.long),
            "scores":      torch.zeros((0,)),
            "class_names": [],
        }

    # Step 2: Per-class NMS
    keep   = apply_nms_per_class(boxes, scores, labels, nms_thresh)
    boxes  = boxes[keep]
    labels = labels[keep]
    scores = scores[keep]

    # Step 3: Clip to image boundary
    boxes  = clip_boxes_to_image(boxes, orig_size)

    # Add human-readable class names
    class_names = [
        LABEL_TO_NAME.get(l.item(), f"cls_{l.item()}")
        for l in labels
    ]

    return {
        "boxes":       boxes,
        "labels":      labels,
        "scores":      scores,
        "class_names": class_names,
    }


# ── Visualisation ─────────────────────────────────────────────────────────────

def draw_detections_cv2(
    frame:       np.ndarray,
    detections:  dict,
    show_scores: bool = True,
) -> np.ndarray:
    """
    Draw bounding boxes on a BGR frame using OpenCV.

    Args:
        frame      : BGR numpy array
        detections : postprocessed detection dict
        show_scores: whether to show confidence scores

    Returns:
        annotated frame (copy)
    """
    out = frame.copy()

    for box, label, score, name in zip(
        detections["boxes"],
        detections["labels"],
        detections["scores"],
        detections["class_names"],
    ):
        x1, y1, x2, y2 = box.int().tolist()
        color = CLASS_COLORS_BGR.get(name, DEFAULT_COLOR)

        # Draw box
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)

        # Draw label background + text
        label_text = f"{name} {score:.2f}" if show_scores else name
        (tw, th), _ = cv2.getTextSize(
            label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1
        )
        cv2.rectangle(
            out,
            (x1, y1 - th - 6),
            (x1 + tw + 4, y1),
            color, -1
        )
        cv2.putText(
            out, label_text,
            (x1 + 2, y1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55, (0, 0, 0), 1
        )

    return out


def draw_stats_overlay(
    frame:      np.ndarray,
    detections: dict,
    fps:        float = 0.0,
) -> np.ndarray:
    """Draw HUD with detection counts and FPS."""
    out   = frame.copy()
    H, W  = frame.shape[:2]

    # Count per class
    from collections import Counter
    counts = Counter(detections["class_names"])

    # Background panel
    panel_h = 20 + len(counts) * 22 + 30
    cv2.rectangle(out, (8, 8), (200, panel_h), (0, 0, 0), -1)
    cv2.rectangle(out, (8, 8), (200, panel_h), (100,100,100), 1)

    # FPS
    cv2.putText(out, f"FPS: {fps:.1f}",
                (14, 28), cv2.FONT_HERSHEY_SIMPLEX,
                0.55, (0, 255, 255), 1)

    # Counts per class
    y = 50
    for name, count in sorted(counts.items()):
        color = CLASS_COLORS_BGR.get(name, DEFAULT_COLOR)
        cv2.putText(out, f"{name}: {count}",
                    (14, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, color, 1)
        y += 22

    # Total
    cv2.putText(out, f"Total: {len(detections['boxes'])}",
                (14, y + 4), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (255, 255, 255), 1)

    return out


# ── Core inference functions ──────────────────────────────────────────────────

def run_on_image(
    model:        torch.nn.Module,
    image_path:   str,
    device:       torch.device,
    score_thresh: float = 0.5,
    save_path:    str   = None,
) -> dict:
    """
    Run inference on a single image file.

    Args:
        model       : loaded FasterRCNN model (eval mode)
        image_path  : path to image file
        device      : torch device
        score_thresh: confidence threshold
        save_path   : if given, save annotated image here

    Returns:
        detections dict
    """
    # Preprocess
    tensor, orig_size = preprocess_image(image_path)
    tensor = tensor.to(device)

    # Inference
    with torch.no_grad():
        outputs = model([tensor])

    # Postprocess
    dets = postprocess_detections(
        outputs[0], orig_size, score_thresh
    )

    # Visualise
    frame = cv2.imread(image_path)
    frame = draw_detections_cv2(frame, dets)
    frame = draw_stats_overlay(frame, dets)

    if save_path:
        cv2.imwrite(save_path, frame)
        print(f"  Saved → {save_path}")

    return dets, frame


def run_on_video(
    model:        torch.nn.Module,
    source,
    device:       torch.device,
    score_thresh: float = 0.5,
    save_path:    str   = None,
    display:      bool  = True,
):
    """
    Run inference on video file or webcam stream.

    Args:
        model       : loaded FasterRCNN model (eval mode)
        source      : video path (str) or camera index (int)
        device      : torch device
        score_thresh: confidence threshold
        save_path   : save annotated video here (optional)
        display     : show live window
    """
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open source: {source}")

    W   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25

    writer = None
    if save_path:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(save_path, fourcc, fps, (W, H))

    frame_count = 0
    fps_history = []

    print(f"  Running on {'webcam' if isinstance(source, int) else source}")
    print(f"  Press Q to quit\n")

    try:
        while cap.isOpened():
            t0  = time.time()
            ok, frame = cap.read()
            if not ok:
                break

            # Preprocess
            tensor, orig_size = preprocess_image(frame)
            tensor = tensor.to(device)

            # Inference
            with torch.no_grad():
                outputs = model([tensor])

            # Postprocess
            dets  = postprocess_detections(
                outputs[0], orig_size, score_thresh
            )

            # Draw
            frame = draw_detections_cv2(frame, dets)

            # FPS
            elapsed = time.time() - t0
            fps_history.append(1.0 / (elapsed + 1e-9))
            fps_history = fps_history[-30:]
            avg_fps     = np.mean(fps_history)

            frame = draw_stats_overlay(frame, dets, fps=avg_fps)

            if writer:
                writer.write(frame)

            if display:
                cv2.imshow("Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            frame_count += 1

    finally:
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        print(f"\n  Processed {frame_count} frames")
        if save_path:
            print(f"  Saved → {save_path}")


def load_model_for_inference(
    checkpoint_path: str,
    device:          torch.device,
    num_classes:     int = None,
) -> torch.nn.Module:
    """
    Load a trained model from checkpoint for inference.

    Args:
        checkpoint_path : path to .pth checkpoint
        device          : torch device
        num_classes     : override num_classes (uses config default if None)

    Returns:
        model in eval mode on device
    """
    num_classes = num_classes or cfg.NUM_CLASSES

    model = build_detector(
        num_classes         = num_classes,
        backbone_name       = cfg.BACKBONE,
        pretrained_backbone = False,   # we load our own weights
    ).to(device)

    if checkpoint_path and os.path.exists(checkpoint_path):
        print(f"  Loading checkpoint: {checkpoint_path}")
        ckpt = torch.load(checkpoint_path, map_location=device)

        # Handle both raw state dict and full checkpoint
        if "model_state" in ckpt:
            model.load_state_dict(ckpt["model_state"])
            epoch = ckpt.get("epoch", "?")
            loss  = ckpt.get("val_loss", "?")
            print(f"  Loaded epoch={epoch}, val_loss={loss}")
        else:
            model.load_state_dict(ckpt)
            print(f"  Loaded raw state dict")
    else:
        print(f"  WARNING: No checkpoint — using random weights")

    model.eval()
    print(f"  Model ready on {device}\n")
    return model


# ── CLI entry point ───────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--source",     required=True,
                   help="Image/video path, folder, or camera index (0)")
    p.add_argument("--checkpoint", default=None,
                   help="Path to trained checkpoint")
    p.add_argument("--score-thr",  type=float,
                   default=cfg.SCORE_THRESHOLD)
    p.add_argument("--save",       type=str, default=None,
                   help="Save output to this path")
    p.add_argument("--no-display", action="store_true")
    return p.parse_args()


if __name__ == "__main__":
    args   = parse_args()
    device = torch.device(cfg.DEVICE)

    model = load_model_for_inference(
        args.checkpoint, device
    )

    source = args.source

    # Detect source type
    if source.isdigit():
        # Webcam
        run_on_video(model, int(source), device,
                     args.score_thr, args.save,
                     display=not args.no_display)

    elif os.path.isfile(source):
        ext = Path(source).suffix.lower()
        if ext in (".jpg", ".jpeg", ".png", ".bmp"):
            # Single image
            dets, frame = run_on_image(
                model, source, device,
                args.score_thr, args.save
            )
            print(f"\n  Detections: {len(dets['boxes'])}")
            for name, score in zip(dets["class_names"],
                                    dets["scores"]):
                print(f"    {name:<15} {score:.3f}")
            if not args.no_display:
                cv2.imshow("Detection", frame)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        else:
            # Video
            run_on_video(model, source, device,
                         args.score_thr, args.save,
                         display=not args.no_display)

    elif os.path.isdir(source):
        # Folder of images
        exts  = {".jpg", ".jpeg", ".png", ".bmp"}
        files = [f for f in os.listdir(source)
                 if Path(f).suffix.lower() in exts]
        print(f"  Found {len(files)} images in {source}\n")

        os.makedirs(args.save or "outputs", exist_ok=True)
        for fname in files:
            fpath = os.path.join(source, fname)
            out   = os.path.join(
                args.save or "outputs", fname
            )
            dets, _ = run_on_image(
                model, fpath, device, args.score_thr, out
            )
            print(f"  {fname}: {len(dets['boxes'])} detections")