# utils/dual_inference.py
"""
Dual Model Inference
─────────────────────
Runs both models on the same frame and
combines their outputs into one result.

Model 1 → persons + vehicles + density
Model 2 → accident detection
       ↓
Combined output → unified alert engine
"""

import torch
import numpy as np
from dataclasses import dataclass, field
from typing      import List, Dict, Tuple, Optional


@dataclass
class CombinedDetectionResult:
    """
    Final output combining both models.
    """
    # From Model 1
    person_boxes:   torch.Tensor = None
    vehicle_boxes:  torch.Tensor = None
    person_count:   int          = 0
    vehicle_count:  int          = 0
    grid_occupancy: float        = 0.0
    hotspots:       list         = field(default_factory=list)

    # From Model 2
    accident_boxes:     torch.Tensor = None
    accident_scores:    torch.Tensor = None
    accident_detected:  bool         = False

    # Combined
    all_boxes:      torch.Tensor = None
    all_labels:     torch.Tensor = None
    all_scores:     torch.Tensor = None
    all_names:      list         = field(default_factory=list)

    # Alert levels
    alerts: list = field(default_factory=list)


class DualModelInference:
    """
    Manages two models and combines their outputs.

    Args:
        model1          : trained person+vehicle detector
        model2          : trained accident detector
        device          : torch device
        score_thresh1   : confidence threshold model 1
        score_thresh2   : confidence threshold model 2
    """

    def __init__(
        self,
        model1,
        model2,
        device,
        score_thresh1: float = 0.5,
        score_thresh2: float = 0.6,
    ):
        self.model1        = model1
        self.model2        = model2
        self.device        = device
        self.score_thresh1 = score_thresh1
        self.score_thresh2 = score_thresh2

        # Put both in eval mode
        self.model1.eval()
        self.model2.eval()

        print("[DualModel] Both models loaded and ready")

    @torch.no_grad()
    def run(
        self,
        frame_tensor: torch.Tensor,
        frame_hw:     Tuple[int, int],
    ) -> CombinedDetectionResult:
        """
        Run both models on one frame.

        Args:
            frame_tensor : preprocessed [3,H,W] tensor
            frame_hw     : (H, W) of original frame

        Returns:
            CombinedDetectionResult
        """
        from torch.amp import autocast
        from inference import postprocess_detections
        from utils.density import (
            detections_from_model_output,
            build_grid_density,
        )
        from dataset.coco_dataset import LABEL_TO_NAME

        inp = [frame_tensor.to(self.device)]

        # ── Model 1: Person + Vehicle ──────────────────
        with autocast("cuda",
                      enabled=(self.device.type=="cuda")):
            out1 = self.model1(inp)

        dets1 = postprocess_detections(
            out1[0], frame_hw,
            score_thresh = self.score_thresh1,
        )

        det_results1 = detections_from_model_output(dets1)
        persons  = [d for d in det_results1
                    if d.class_name == "person"]
        vehicles = [d for d in det_results1
                    if d.class_name in (
                        "car","truck","bus",
                        "motorcycle","bicycle")]

        # Grid density
        grid = build_grid_density(
            det_results1, frame_hw,
            cell_size      = 64,
            hotspot_thresh = 3,
            class_filter   = ["person"],
        )

        # ── Model 2: Accident ──────────────────────────
        with autocast("cuda",
                      enabled=(self.device.type=="cuda")):
            out2 = self.model2(inp)

        dets2 = postprocess_detections(
            out2[0], frame_hw,
            score_thresh = self.score_thresh2,
        )

        accident_detected = len(dets2["boxes"]) > 0

        # ── Combine outputs ────────────────────────────
        # Merge all boxes for visualization
        all_boxes  = []
        all_labels = []
        all_scores = []
        all_names  = []

        if len(dets1["boxes"]) > 0:
            all_boxes.append(dets1["boxes"])
            all_labels.append(dets1["labels"])
            all_scores.append(dets1["scores"])
            all_names.extend(dets1["class_names"])

        if len(dets2["boxes"]) > 0:
            all_boxes.append(dets2["boxes"])
            all_labels.append(dets2["labels"])
            all_scores.append(dets2["scores"])
            all_names.extend(
                ["accident"] * len(dets2["boxes"])
            )

        combined_boxes  = (torch.cat(all_boxes)
                           if all_boxes
                           else torch.zeros((0,4)))
        combined_labels = (torch.cat(all_labels)
                           if all_labels
                           else torch.zeros((0,),
                               dtype=torch.long))
        combined_scores = (torch.cat(all_scores)
                           if all_scores
                           else torch.zeros((0,)))

        return CombinedDetectionResult(
            person_boxes       = dets1["boxes"][
                dets1["labels"] == 1
            ] if len(dets1["boxes"]) > 0
              else torch.zeros((0,4)),
            vehicle_boxes      = dets1["boxes"][
                dets1["labels"] != 1
            ] if len(dets1["boxes"]) > 0
              else torch.zeros((0,4)),
            person_count       = len(persons),
            vehicle_count      = len(vehicles),
            grid_occupancy     = grid.occupancy,
            hotspots           = grid.hotspots,
            accident_boxes     = dets2["boxes"],
            accident_scores    = dets2["scores"],
            accident_detected  = accident_detected,
            all_boxes          = combined_boxes,
            all_labels         = combined_labels,
            all_scores         = combined_scores,
            all_names          = all_names,
        )

    @classmethod
    def load(
        cls,
        checkpoint1: str,
        checkpoint2: str,
        device,
        num_classes1: int = 7,
        num_classes2: int = 2,
    ):
        """
        Load both models from checkpoints.

        Args:
            checkpoint1  : path to model1 checkpoint
            checkpoint2  : path to model2 checkpoint
            device       : torch device
            num_classes1 : classes for model1 (default 7)
            num_classes2 : classes for model2 (default 2)
        """
        from model.detector import build_detector
        from inference      import load_model_for_inference

        print("[DualModel] Loading Model 1 "
              "(person+vehicle)...")
        model1 = load_model_for_inference(
            checkpoint1, device, num_classes1
        )

        print("[DualModel] Loading Model 2 "
              "(accident)...")
        model2 = load_model_for_inference(
            checkpoint2, device, num_classes2
        )

        return cls(model1, model2, device)